from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.hashers import check_password  # PENTING: Impor fungsi check_password
from .models import Produk, Pelanggan, Pemesanan, Produksi, DetailProduksi, Karyawan
from .admin import admin_dashboard_context


@staff_member_required
def admin_dashboard(request):
    # Get dashboard context data
    context = admin_dashboard_context()
    return render(request, 'admin/index.html', context)


def karyawan_login(request):
    if request.session.get('karyawan_id'):
        return redirect('core:karyawan_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')  # Password yang dimasukkan pengguna (plain text)
        
        try:
            karyawan = Karyawan.objects.get(username=username)
        except Karyawan.DoesNotExist:
            karyawan = None

        # PENTING: Gunakan check_password
        # Membandingkan password plain text (input pengguna) dengan password hash (dari DB)
        if karyawan and check_password(password, karyawan.password):
            # Login Berhasil: Set session
            request.session['karyawan_id'] = karyawan.idKaryawan
            request.session['karyawan_nama'] = karyawan.nama
            messages.success(request, f"Selamat datang, {karyawan.nama}!")
            return redirect('core:karyawan_dashboard')
        else:
            messages.error(request, "Username atau Password salah.")
            
    return render(request, 'karyawan/karyawan_login.html')


def karyawan_logout(request):
    # Remove karyawan_id from session
    if 'karyawan_id' in request.session:
        del request.session['karyawan_id']
    if 'karyawan_nama' in request.session:
        del request.session['karyawan_nama']
    messages.info(request, "Anda telah logout.")
    return redirect('core:karyawan_login')


def karyawan_dashboard(request):
    # Check if karyawan is logged in
    if not request.session.get('karyawan_id'):
        messages.warning(request, "Anda harus login terlebih dahulu.")
        return redirect('core:karyawan_login')
    
    karyawan_id = request.session.get('karyawan_id')
    
    # Get karyawan object
    try:
        karyawan = Karyawan.objects.get(idKaryawan=karyawan_id)
    except Karyawan.DoesNotExist:
        messages.error(request, "Data karyawan tidak ditemukan.")
        return redirect('core:karyawan_login')
    
    # Get bahan baku for the modal
    bahan_baku = Produk.objects.filter(jenisProduk='Bahan Baku').order_by('namaProduk')
    
    # Get recent productions by this karyawan
    recent_productions = Produksi.objects.filter(idKaryawan=karyawan).order_by('-tanggalProduksi')[:10]
    
    # Calculate production statistics
    total_productions = Produksi.objects.filter(idKaryawan=karyawan).count()
    total_tahu = Produksi.objects.filter(idKaryawan=karyawan, jenisHasil='Tahu').count()
    total_tempe = Produksi.objects.filter(idKaryawan=karyawan, jenisHasil='Tempe').count()
    
    context = {
        'karyawan': karyawan,
        'bahan_baku': bahan_baku,
        'recent_productions': recent_productions,
        'total_productions': total_productions,
        'total_tahu': total_tahu,
        'total_tempe': total_tempe,
    }
    
    return render(request, 'karyawan/karyawan_dashboard.html', context)


def karyawan_produksi_input(request):
    if not request.session.get('karyawan_id'):
        messages.warning(request, "Anda harus login.")
        return redirect('core:karyawan_login')
    
    karyawan_id = request.session.get('karyawan_id')
    
    if request.method == 'POST':
        # --- Data Produksi Utama ---
        tanggalProduksi = request.POST.get('tanggalProduksi')
        jenisHasil = request.POST.get('jenisHasil')
        jumlahHasil = request.POST.get('jumlahHasil')
        satuanHasil = request.POST.get('satuanHasil')
        keterangan = request.POST.get('keterangan')

        # --- Data Detail Produksi (Bahan Baku) ---
        produk_ids = request.POST.getlist('idProduk[]')
        jumlah_terpakai = request.POST.getlist('jumlahBahanTerpakai[]')
        
        try:
            with transaction.atomic():
                # 1. Simpan Data Produksi Utama
                new_produksi = Produksi(
                    tanggalProduksi=tanggalProduksi,
                    jenisHasil=jenisHasil,
                    jumlahHasil=jumlahHasil,
                    satuanHasil=satuanHasil,
                    keterangan=keterangan,
                    idKaryawan_id=karyawan_id  # Hubungkan ke Karyawan yang sedang login
                )
                new_produksi.save()
                
                # 2. Simpan Detail Produksi (Menggunakan clean/save logic di Model)
                for prod_id, jml_terpakai in zip(produk_ids, jumlah_terpakai):
                    if jml_terpakai and int(jml_terpakai) > 0:
                        DetailProduksi.objects.create(
                            idProduksi=new_produksi,
                            idProduk_id=prod_id,
                            jumlahBahanTerpakai=int(jml_terpakai)
                        )
                
            messages.success(request, f"Produksi {jenisHasil} berhasil dicatat!")
            return redirect('core:karyawan_dashboard')

        except Exception as e:
            messages.error(request, f"Gagal mencatat produksi: {e}")
            return redirect('core:karyawan_dashboard')
            
    # Jika request GET, tidak ada yang dilakukan di sini, Modal akan ditampilkan dari template
    pass