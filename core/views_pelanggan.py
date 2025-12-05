from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
import json
from .models import Pelanggan, Produk, Pemesanan, DetailPemesanan
from django.db import models


def pelanggan_register(request):
    """Register a new customer"""
    if request.method == 'POST':
        nama = request.POST.get('nama')
        alamat = request.POST.get('alamat')
        no_telp = request.POST.get('no_telp')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not all([nama, alamat, no_telp, username, password]):
            messages.error(request, "Semua field harus diisi.")
            return render(request, 'pelanggan/register.html')
            
        if password != confirm_password:
            messages.error(request, "Password dan konfirmasi password tidak cocok.")
            return render(request, 'pelanggan/register.html')
            
        if len(password) < 6:
            messages.error(request, "Password minimal 6 karakter.")
            return render(request, 'pelanggan/register.html')
            
        # Check if username already exists
        if Pelanggan.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan.")
            return render(request, 'pelanggan/register.html')
            
        # Create new customer
        try:
            pelanggan = Pelanggan(
                namaPelanggan=nama,
                alamat=alamat,
                noTelp=no_telp,
                username=username,
                password=password  # Will be hashed in model save method
            )
            pelanggan.save()
            messages.success(request, "Registrasi berhasil! Silakan login.")
            return redirect('pelanggan_login')
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")
            return render(request, 'pelanggan/register.html')
            
    return render(request, 'pelanggan/register.html')


def pelanggan_login(request):
    """Customer login"""
    # If already logged in, redirect to dashboard
    if request.session.get('pelanggan_id'):
        return redirect('pelanggan_beranda')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            pelanggan = Pelanggan.objects.get(username=username)
        except Pelanggan.DoesNotExist:
            pelanggan = None
            
        # Check password
        if pelanggan and check_password(password, pelanggan.password):
            # Login successful
            request.session['pelanggan_id'] = pelanggan.idPelanggan
            request.session['pelanggan_nama'] = pelanggan.namaPelanggan
            messages.success(request, f"Selamat datang, {pelanggan.namaPelanggan}!")
            return redirect('pelanggan_beranda')
        else:
            messages.error(request, "Username atau Password salah.")
            
    return render(request, 'pelanggan/login.html')


def pelanggan_logout(request):
    """Customer logout"""
    if 'pelanggan_id' in request.session:
        del request.session['pelanggan_id']
    if 'pelanggan_nama' in request.session:
        del request.session['pelanggan_nama']
    if 'keranjang' in request.session:
        del request.session['keranjang']
    messages.info(request, "Anda telah logout.")
    return redirect('pelanggan_login')


def get_pelanggan(request):
    """Helper function to get current logged in customer"""
    pelanggan_id = request.session.get('pelanggan_id')
    if not pelanggan_id:
        return None
    try:
        return Pelanggan.objects.get(idPelanggan=pelanggan_id)
    except Pelanggan.DoesNotExist:
        return None


def pelanggan_required(view_func):
    """Decorator to ensure customer is logged in"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('pelanggan_id'):
            messages.warning(request, "Anda harus login terlebih dahulu.")
            return redirect('pelanggan_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@pelanggan_required
def pelanggan_beranda(request):
    """Customer dashboard/homepage"""
    pelanggan = get_pelanggan(request)
    
    # Get notifications for orders with shipping costs > 0
    notifications = Pemesanan.objects.filter(
        idPelanggan=pelanggan,
        ongkosKirim__gt=0,
        status__in=['Diproses', 'Menunggu Pembayaran']
    )
    
    # Get products for display
    bahan_baku = Produk.objects.filter(jenisProduk='Bahan Baku', stok__gt=0)[:4]  # Limit to 4 items
    produk_jadi = Produk.objects.filter(jenisProduk='Produk Jadi', stok__gt=0)[:4]  # Limit to 4 items
    
    context = {
        'bahan_baku': bahan_baku,
        'produk_jadi': produk_jadi,
        'notifications': notifications
    }
    return render(request, 'pelanggan/beranda.html', context)


@pelanggan_required
def pelanggan_produk_list(request):
    """List all available products"""
    # Get only available products (stok > 0)
    produk_jadi = Produk.objects.filter(jenisProduk='Produk Jadi', stok__gt=0).order_by('namaProduk')
    
    context = {
        'produk_jadi': produk_jadi
    }
    return render(request, 'pelanggan/produk_list.html', context)


def get_cart(request):
    """Helper function to get cart from session"""
    if 'keranjang' not in request.session:
        request.session['keranjang'] = {}
    return request.session['keranjang']


def save_cart(request, cart):
    """Helper function to save cart to session"""
    request.session['keranjang'] = cart
    request.session.modified = True


@pelanggan_required
def pelanggan_keranjang_add(request):
    """Add product to cart"""
    if request.method == 'POST':
        try:
            produk_id = int(request.POST.get('produk_id'))
            kuantiti = int(request.POST.get('kuantiti', 1))
            
            # Validate product
            try:
                produk = Produk.objects.get(idProduk=produk_id, jenisProduk='Produk Jadi')
            except Produk.DoesNotExist:
                messages.error(request, 'Produk tidak ditemukan.')
                return redirect('pelanggan_keranjang_view')
                
            # Check stock
            if kuantiti > produk.stok:
                messages.error(request, f'Stok tidak mencukupi. Tersedia: {produk.stok}')
                return redirect('pelanggan_keranjang_view')
                
            # Get cart
            cart = get_cart(request)
            
            # Add to cart
            if str(produk_id) in cart:
                # Check if adding this quantity would exceed stock
                new_quantity = cart[str(produk_id)]['kuantiti'] + kuantiti
                if new_quantity > produk.stok:
                    messages.error(request, f'Stok tidak mencukupi. Maksimal: {produk.stok}')
                    return redirect('pelanggan_keranjang_view')
                cart[str(produk_id)]['kuantiti'] = new_quantity
            else:
                cart[str(produk_id)] = {
                    'nama': produk.namaProduk,
                    'harga': produk.harga,
                    'kuantiti': kuantiti,
                    'stok': produk.stok
                }
                
            # Save cart
            save_cart(request, cart)
            
            messages.success(request, f'{produk.namaProduk} berhasil ditambahkan ke keranjang!')
            return redirect('pelanggan_produk_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('pelanggan_keranjang_view')
            
    return redirect('pelanggan_keranjang_view')


@pelanggan_required
def pelanggan_keranjang_update(request):
    """Update cart item quantity"""
    if request.method == 'POST':
        try:
            produk_id = str(request.POST.get('produk_id'))
            kuantiti = int(request.POST.get('kuantiti', 0))
            
            # Get cart
            cart = get_cart(request)
            
            # Validate product exists in cart
            if produk_id not in cart:
                messages.error(request, 'Item tidak ditemukan di keranjang.')
                return redirect('pelanggan_keranjang_view')
                
            # Validate product
            try:
                produk = Produk.objects.get(idProduk=produk_id, jenisProduk='Produk Jadi')
            except Produk.DoesNotExist:
                messages.error(request, 'Produk tidak ditemukan.')
                return redirect('pelanggan_keranjang_view')
                
            # Handle removal
            if kuantiti <= 0:
                del cart[produk_id]
                save_cart(request, cart)
                messages.success(request, 'Item dihapus dari keranjang.')
                return redirect('pelanggan_keranjang_view')
                
            # Check stock
            if kuantiti > produk.stok:
                messages.error(request, f'Stok tidak mencukupi. Tersedia: {produk.stok}')
                return redirect('pelanggan_keranjang_view')
                
            # Update quantity
            cart[produk_id]['kuantiti'] = kuantiti
            save_cart(request, cart)
            
            messages.success(request, 'Keranjang diperbarui.')
            return redirect('pelanggan_keranjang_view')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('pelanggan_keranjang_view')
            
    return redirect('pelanggan_keranjang_view')


@pelanggan_required
def pelanggan_keranjang_delete(request):
    """Remove item from cart"""
    if request.method == 'POST':
        try:
            produk_id = str(request.POST.get('produk_id'))
            
            # Get cart
            cart = get_cart(request)
            
            # Remove item
            if produk_id in cart:
                del cart[produk_id]
                save_cart(request, cart)
                messages.success(request, 'Item dihapus dari keranjang.')
                return redirect('pelanggan_keranjang_view')
            else:
                messages.error(request, 'Item tidak ditemukan di keranjang.')
                return redirect('pelanggan_keranjang_view')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('pelanggan_keranjang_view')
            
    return redirect('pelanggan_keranjang_view')


@pelanggan_required
def pelanggan_keranjang_view(request):
    """View shopping cart"""
    cart = get_cart(request)
    
    # Enrich cart data with product info
    cart_items = []
    total_keranjang = 0
    
    for produk_id, item in cart.items():
        try:
            produk = Produk.objects.get(idProduk=produk_id)
            subtotal = item['kuantiti'] * item['harga']
            total_keranjang += subtotal
            
            cart_items.append({
                'produk_id': produk_id,
                'nama': item['nama'],
                'harga': item['harga'],
                'kuantiti': item['kuantiti'],
                'stok': item['stok'],
                'subtotal': subtotal,
                'produk_obj': produk
            })
        except Produk.DoesNotExist:
            # Remove invalid products from cart
            continue
    
    context = {
        'cart_items': cart_items,
        'total_keranjang': total_keranjang
    }
    return render(request, 'pelanggan/keranjang.html', context)


@pelanggan_required
def pelanggan_checkout_view(request):
    """Display checkout page"""
    # Get cart items
    cart = get_cart(request)
    if not cart:
        messages.error(request, "Keranjang Anda kosong.")
        return redirect('pelanggan_produk_list')
    
    # Calculate total
    total_keranjang = sum(item['kuantiti'] * item['harga'] for item in cart.values())
    
    context = {
        'total_keranjang': total_keranjang
    }
    return render(request, 'pelanggan/checkout.html', context)


@pelanggan_required
def pelanggan_checkout(request):
    """Process checkout"""
    if request.method == 'POST':
        # Debugging: Log received POST data
        print(f"Received POST data: {request.POST}")
        print(f"Received FILES data: {request.FILES}")
        
        # Get customer
        pelanggan = get_pelanggan(request)
        if not pelanggan:
            messages.error(request, 'Pelanggan tidak ditemukan.')
            return redirect('pelanggan_login')
            
        # Get cart
        cart = get_cart(request)
        if not cart:
            messages.error(request, 'Keranjang kosong.')
            return redirect('pelanggan_keranjang_view')
            
        # Explicit validation for required fields
        alamat_pengiriman = request.POST.get('alamat_pengiriman')
        bukti_bayar = request.FILES.get('bukti_bayar')
        
        # Debugging: Log extracted values
        print(f"Alamat pengiriman: {alamat_pengiriman}")
        print(f"Bukti bayar: {bukti_bayar}")
        
        # Validate required fields
        if not alamat_pengiriman or not alamat_pengiriman.strip():
            messages.error(request, 'Alamat pengiriman wajib diisi.')
            return redirect('pelanggan_checkout_view')
            
        if not bukti_bayar:
            messages.error(request, 'Bukti pembayaran wajib diunggah.')
            return redirect('pelanggan_checkout_view')
            
        try:
            with transaction.atomic():
                # Calculate total
                total_pemesanan = sum(item['kuantiti'] * item['harga'] for item in cart.values())
                
                # Debugging: Log calculated total
                print(f"Calculated total: {total_pemesanan}")
                
                # Create order
                pemesanan = Pemesanan.objects.create(
                    tanggalPemesanan=timezone.now().date(),
                    totalPemesanan=total_pemesanan,
                    idPelanggan=pelanggan,
                    alamatPengiriman=alamat_pengiriman,
                    buktiBayar=bukti_bayar
                )
                
                # Debugging: Log created order
                print(f"Created order: {pemesanan.idPemesanan}")
                
                # Create order details and update stock
                for produk_id, item in cart.items():
                    produk = Produk.objects.get(idProduk=produk_id)
                    kuantiti = item['kuantiti']
                    subtotal = kuantiti * item['harga']
                    
                    # Debugging: Log item details
                    print(f"Processing item - Product ID: {produk_id}, Quantity: {kuantiti}, Subtotal: {subtotal}")
                    
                    # Check stock again
                    if kuantiti > produk.stok:
                        messages.error(request, f'Stok untuk {produk.namaProduk} tidak mencukupi. Tersedia: {produk.stok}')
                        return redirect('pelanggan_checkout_view')
                    
                    # Create detail
                    detail = DetailPemesanan.objects.create(
                        idProduk=produk,
                        kuantiti=kuantiti,
                        subTotal=subtotal,
                        idKoleksiPemesanan=pemesanan
                    )
                    
                    # Debugging: Log created detail
                    print(f"Created detail: {detail.idDetailPemesanan}")
                    
                    # Update stock - Critical business logic
                    old_stock = produk.stok
                    produk.stok -= kuantiti
                    produk.save()
                    
                    # Debugging: Log stock update
                    print(f"Updated stock for {produk.namaProduk}: {old_stock} -> {produk.stok}")
                
                # Clear cart only after successful order creation and stock updates
                request.session['keranjang'] = {}
                request.session.modified = True
                
                # Debugging: Log cart clearance
                print("Cart cleared successfully")
                
            messages.success(request, 'Pesanan berhasil dikirim. Menunggu konfirmasi Admin.')
            return redirect('pelanggan_pesanan_riwayat')
        except Exception as e:
            # Log the full exception for debugging
            print(f"Exception during checkout: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            messages.error(request, f'Gagal memproses pesanan: {str(e)}')
            return redirect('pelanggan_checkout_view')
            
    # If request is not POST, redirect to checkout view
    return redirect('pelanggan_checkout_view')


@pelanggan_required
def pelanggan_pesanan_riwayat(request):
    """View order history"""
    pelanggan = get_pelanggan(request)
    if not pelanggan:
        messages.error(request, "Pelanggan tidak ditemukan.")
        return redirect('pelanggan_login')
        
    # Get all orders for this customer
    pesanan_list = Pemesanan.objects.filter(idPelanggan=pelanggan).order_by('-tanggalPemesanan')
    
    context = {
        'pesanan_list': pesanan_list
    }
    return render(request, 'pelanggan/pesanan_riwayat.html', context)


@pelanggan_required
def pelanggan_pesanan_detail(request, pesanan_id):
    """Get order details via AJAX"""
    if request.method == 'GET':
        try:
            pelanggan = get_pelanggan(request)
            if not pelanggan:
                return JsonResponse({'success': False, 'message': 'Pelanggan tidak ditemukan.'})
                
            # Get order with details
            pemesanan = Pemesanan.objects.select_related('idPelanggan').prefetch_related('detailpemesanan_set__idProduk').get(
                idPemesanan=pesanan_id, 
                idPelanggan=pelanggan
            )
            
            # Prepare order details
            detail_items = []
            for detail in pemesanan.detailpemesanan_set.all():
                detail_items.append({
                    'produk_nama': detail.idProduk.namaProduk,
                    'kuantiti': detail.kuantiti,
                    'harga': detail.idProduk.harga,
                    'subtotal': detail.subTotal
                })
                
            return JsonResponse({
                'success': True,
                'order': {
                    'id': pemesanan.idPemesanan,
                    'tanggal': pemesanan.tanggalPemesanan.strftime('%d/%m/%Y'),
                    'total': pemesanan.totalPemesanan,
                    'status': pemesanan.status,
                    'alamat': pemesanan.keterangan,
                    'items': detail_items
                }
            })
        except Pemesanan.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pesanan tidak ditemukan.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Terjadi kesalahan: {str(e)}'})
            
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@pelanggan_required
def pelanggan_pesanan_detail_html(request, pesanan_id):
    """Show order detail page"""
    try:
        pelanggan = get_pelanggan(request)
        if not pelanggan:
            messages.error(request, "Pelanggan tidak ditemukan.")
            return redirect('pelanggan_login')
            
        # Get order with details
        pemesanan = Pemesanan.objects.select_related('idPelanggan').prefetch_related('detailpemesanan_set__idProduk').get(
            idPemesanan=pesanan_id, 
            idPelanggan=pelanggan
        )
        
        # Prepare order details
        detail_items = []
        for detail in pemesanan.detailpemesanan_set.all():
            detail_items.append({
                'produk_nama': detail.idProduk.namaProduk,
                'kuantiti': detail.kuantiti,
                'harga': detail.idProduk.harga,
                'subtotal': detail.subTotal
            })
            
        context = {
            'pemesanan': pemesanan,
            'detail_items': detail_items
        }
        return render(request, 'pelanggan/pesanan_detail.html', context)
    except Pemesanan.DoesNotExist:
        messages.error(request, "Pesanan tidak ditemukan.")
        return redirect('pelanggan_pesanan_riwayat')
    except Exception as e:
        messages.error(request, f"Terjadi kesalahan: {str(e)}")
        return redirect('pelanggan_pesanan_riwayat')


@pelanggan_required
def pelanggan_akun(request):
    """View and update account information"""
    pelanggan = get_pelanggan(request)
    if not pelanggan:
        messages.error(request, "Pelanggan tidak ditemukan.")
        return redirect('pelanggan_login')
        
    if request.method == 'POST':
        # Update account info
        nama = request.POST.get('nama')
        alamat = request.POST.get('alamat')
        no_telp = request.POST.get('no_telp')
        password_lama = request.POST.get('password_lama')
        password_baru = request.POST.get('password_baru')
        konfirmasi_password = request.POST.get('konfirmasi_password')
        
        # Update basic info
        pelanggan.namaPelanggan = nama
        pelanggan.alamat = alamat
        pelanggan.noTelp = no_telp
        
        # Change password if requested
        if password_lama and password_baru:
            if not check_password(password_lama, pelanggan.password):
                messages.error(request, "Password lama salah.")
                return render(request, 'pelanggan/akun.html', {'pelanggan': pelanggan})
                
            if password_baru != konfirmasi_password:
                messages.error(request, "Password baru dan konfirmasi tidak cocok.")
                return render(request, 'pelanggan/akun.html', {'pelanggan': pelanggan})
                
            if len(password_baru) < 6:
                messages.error(request, "Password baru minimal 6 karakter.")
                return render(request, 'pelanggan/akun.html', {'pelanggan': pelanggan})
                
            pelanggan.password = password_baru  # Will be hashed in save method
            
        # Save changes
        try:
            pelanggan.save()
            messages.success(request, "Informasi akun berhasil diperbarui.")
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")
            
        return redirect('pelanggan_akun')
        
    # Calculate total spending
    total_belanja = Pemesanan.objects.filter(
        idPelanggan=pelanggan, 
        status='Selesai'
    ).aggregate(total=models.Sum('totalPemesanan'))['total'] or 0
    
    context = {
        'pelanggan': pelanggan,
        'total_belanja': total_belanja
    }
    return render(request, 'pelanggan/akun.html', context)