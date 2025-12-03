from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from django.utils.safestring import mark_safe  # PENTING: Untuk merender HTML
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.admin import SimpleListFilter
from datetime import timedelta, datetime
from .models import Karyawan, Produk, Produksi, DetailProduksi, Pelanggan, Pemesanan, DetailPemesanan

# Try to import ReportLab
try:
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    site_header = 'MICKEL PRODUCT Administration'
    site_title = 'MICKEL PRODUCT Admin'
    index_title = 'Dashboard'
    index_template = 'admin/index.html'


# Instantiate the custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')


# Register your models here.
class DetailProduksiInline(admin.TabularInline):
    model = DetailProduksi
    extra = 1


@admin.register(Karyawan, site=custom_admin_site)
class KaryawanAdmin(admin.ModelAdmin):
    list_display = ('idKaryawan', 'nama', 'username', 'aksi_ikon')  # Ganti kolom aksi lama dengan ini
    search_fields = ('nama', 'username')
    list_filter = ('nama',)
    ordering = ('idKaryawan',)
    
    @admin.display(description='Aksi')
    def aksi_ikon(self, obj):
        # Asumsi: Menggunakan Font Awesome (fa)
        edit_url = f"/admin/core/karyawan/{obj.pk}/change/"
        delete_url = f"/admin/core/karyawan/{obj.pk}/delete/"
        
        # Style tombol agar sesuai dengan format Admin (warna/ukuran)
        edit_btn = f'<a href="{edit_url}" class="btn btn-sm btn-info" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_btn = f'<a href="{delete_url}" class="btn btn-sm btn-danger" title="Hapus"><i class="fas fa-trash-alt"></i></a>'
        
        # Gunakan mark_safe untuk memastikan Django merender HTML
        return mark_safe(f'{edit_btn} {delete_btn}')


class StokMenipisFilter(SimpleListFilter):
    title = 'Status Stok'
    parameter_name = 'stok_menipis'
    STOK_AMAN_THRESHOLD = 10  # Ambang batas stok menipis

    def lookups(self, request, model_admin):
        # Opsi yang muncul di filter sidebar
        return (
            ('ya', 'Stok Menipis'),
        )

    def queryset(self, request, queryset):
        # Logika filtering: jika 'ya' dipilih, filter produk yang stoknya < threshold
        if self.value() == 'ya':
            return queryset.filter(stok__lt=self.STOK_AMAN_THRESHOLD)
        return queryset


@admin.register(Produk, site=custom_admin_site)
class ProdukAdmin(admin.ModelAdmin):
    list_display = ('idProduk', 'namaProduk', 'jenisProduk', 'formatted_harga', 'stok', 'satuan', 'aksi_ikon')  # Ganti kolom aksi lama dengan ini
    search_fields = ('namaProduk',)
    list_filter = ('jenisProduk', StokMenipisFilter)  # Tambahkan filter kustom di sini
    ordering = ('idProduk',)
    
    def formatted_harga(self, obj):
        return f"Rp {obj.harga:,}"
    formatted_harga.short_description = 'Harga'
    
    @admin.display(description='Aksi')
    def aksi_ikon(self, obj):
        # Asumsi: Menggunakan Font Awesome (fa)
        edit_url = f"/admin/core/produk/{obj.pk}/change/"
        delete_url = f"/admin/core/produk/{obj.pk}/delete/"
        
        # Style tombol agar sesuai dengan format Admin (warna/ukuran)
        edit_btn = f'<a href="{edit_url}" class="btn btn-sm btn-info" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_btn = f'<a href="{delete_url}" class="btn btn-sm btn-danger" title="Hapus"><i class="fas fa-trash-alt"></i></a>'
        
        # Gunakan mark_safe untuk memastikan Django merender HTML
        return mark_safe(f'{edit_btn} {delete_btn}')


@admin.register(Produksi, site=custom_admin_site)
class ProduksiAdmin(admin.ModelAdmin):
    list_display = ('idProduksi', 'tanggalProduksi', 'jenisHasil', 'jumlahHasil', 'idKaryawan', 'aksi_ikon')  # Ganti kolom aksi lama dengan ini
    search_fields = ('jenisHasil',)
    list_filter = ('tanggalProduksi', 'jenisHasil', 'idKaryawan')
    ordering = ('-tanggalProduksi',)
    inlines = [DetailProduksiInline]
    
    @admin.display(description='Aksi')
    def aksi_ikon(self, obj):
        # Asumsi: Menggunakan Font Awesome (fa)
        edit_url = f"/admin/core/produksi/{obj.pk}/change/"
        delete_url = f"/admin/core/produksi/{obj.pk}/delete/"
        
        # Style tombol agar sesuai dengan format Admin (warna/ukuran)
        edit_btn = f'<a href="{edit_url}" class="btn btn-sm btn-info" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_btn = f'<a href="{delete_url}" class="btn btn-sm btn-danger" title="Hapus"><i class="fas fa-trash-alt"></i></a>'
        
        # Gunakan mark_safe untuk memastikan Django merender HTML
        return mark_safe(f'{edit_btn} {delete_btn}')


class DetailPemesananInline(admin.TabularInline):
    model = DetailPemesanan
    extra = 1
    readonly_fields = ('subTotal',)


@admin.register(Pelanggan, site=custom_admin_site)
class PelangganAdmin(admin.ModelAdmin):
    list_display = ('idPelanggan', 'namaPelanggan', 'alamat', 'noTelp', 'username', 'aksi_ikon')  # Ganti kolom aksi lama dengan ini
    search_fields = ('namaPelanggan', 'username')
    list_filter = ('namaPelanggan',)
    ordering = ('idPelanggan',)
    
    @admin.display(description='Aksi')
    def aksi_ikon(self, obj):
        # Asumsi: Menggunakan Font Awesome (fa)
        edit_url = f"/admin/core/pelanggan/{obj.pk}/change/"
        delete_url = f"/admin/core/pelanggan/{obj.pk}/delete/"
        
        # Style tombol agar sesuai dengan format Admin (warna/ukuran)
        edit_btn = f'<a href="{edit_url}" class="btn btn-sm btn-info" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_btn = f'<a href="{delete_url}" class="btn btn-sm btn-danger" title="Hapus"><i class="fas fa-trash-alt"></i></a>'
        
        # Gunakan mark_safe untuk memastikan Django merender HTML
        return mark_safe(f'{edit_btn} {delete_btn}')


@admin.register(Pemesanan, site=custom_admin_site)
class PemesananAdmin(admin.ModelAdmin):
    list_display = ( 'tanggalPemesanan', 'formatted_totalPemesanan', 'idPelanggan', 'status', 'aksi_ikon')  # Ganti kolom aksi lama dengan ini
    search_fields = ('idPelanggan__namaPelanggan',)
    list_filter = ('tanggalPemesanan', 'idPelanggan', 'status')
    ordering = ('-tanggalPemesanan',)
    readonly_fields = ('totalPemesanan',)
    inlines = [DetailPemesananInline]
    
    # Define statuses that trigger stock reduction
    STOCK_REDUCTION_STATUSES = ['Diproses', 'Dikirim', 'Selesai']
    
    def formatted_totalPemesanan(self, obj):
        return f"Rp {obj.totalPemesanan:,}"
    formatted_totalPemesanan.short_description = 'Total Pemesanan'
    
    @admin.display(description='Aksi')
    def aksi_ikon(self, obj):
        # Asumsi: Menggunakan Font Awesome (fa)
        edit_url = f"/admin/core/pemesanan/{obj.pk}/change/"
        delete_url = f"/admin/core/pemesanan/{obj.pk}/delete/"
        
        # Style tombol agar sesuai dengan format Admin (warna/ukuran)
        edit_btn = f'<a href="{edit_url}" class="btn btn-sm btn-info" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_btn = f'<a href="{delete_url}" class="btn btn-sm btn-danger" title="Hapus"><i class="fas fa-trash-alt"></i></a>'
        
        # Gunakan mark_safe untuk memastikan Django merender HTML
        return mark_safe(f'{edit_btn} {delete_btn}')
    
    def save_model(self, request, obj, form, change):
        # Get the old status if this is an update
        old_status = None
        if change:
            old_status = form.initial.get('status')
            
        # Save the object first
        super().save_model(request, obj, form, change)
        
        # Handle stock adjustments based on status changes
        if change:
            new_status = obj.status
            
            # Reduce stock if status changes from inactive to active
            if new_status in self.STOCK_REDUCTION_STATUSES and old_status not in self.STOCK_REDUCTION_STATUSES:
                # When status changes to an active status, reduce stock of finished products
                details = DetailPemesanan.objects.filter(idKoleksiPemesanan=obj)
                for detail in details:
                    if detail.idProduk.jenisProduk == 'Produk Jadi':
                        detail.idProduk.stok -= detail.kuantiti
                        detail.idProduk.save()
            # Restore stock if status changes to 'Dibatalkan'
            elif new_status == 'Dibatalkan' and old_status in self.STOCK_REDUCTION_STATUSES:
                # When status changes to 'Dibatalkan', restore stock
                details = DetailPemesanan.objects.filter(idKoleksiPemesanan=obj)
                for detail in details:
                    if detail.idProduk.jenisProduk == 'Produk Jadi':
                        detail.idProduk.stok += detail.kuantiti
                        detail.idProduk.save()
        else:
            # For new objects, reduce stock if status is active
            if obj.status in self.STOCK_REDUCTION_STATUSES:
                details = DetailPemesanan.objects.filter(idKoleksiPemesanan=obj)
                for detail in details:
                    if detail.idProduk.jenisProduk == 'Produk Jadi':
                        detail.idProduk.stok -= detail.kuantiti
                        detail.idProduk.save()
    
    def save_formset(self, request, form, formset, change):
        # Save the formset first
        formset.save()
        
        # Calculate total from details
        total = formset.instance.detailpemesanan_set.aggregate(
            total=Sum('subTotal')
        )['total'] or 0
        
        # Update the parent object
        formset.instance.totalPemesanan = total
        formset.instance.save()


# Filter view functions
@staff_member_required
def report_filter_penjualan(request):
    # Logika untuk mendapatkan status choices (dari model Pemesanan) jika perlu
    context = {'title': 'Filter Laporan Penjualan', 'status_choices': Pemesanan.STATUS_CHOICES}
    
    filtered_data = None
    
    if request.method == 'POST':
        # Dapatkan filter dari POST request
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        status = request.POST.get('status')
        
        # Lakukan filtering pada model Pemesanan
        queryset = Pemesanan.objects.all()
        
        if date_from:
            queryset = queryset.filter(tanggalPemesanan__gte=date_from)
        if date_to:
            queryset = queryset.filter(tanggalPemesanan__lte=date_to)
        if status:
            queryset = queryset.filter(status=status)
            
        filtered_data = queryset.order_by('-tanggalPemesanan')
        
        # Kirim filter yang sudah disubmit kembali ke template untuk mempertahankan nilai form
        context['submitted_filters'] = request.POST
        context['filtered_data'] = filtered_data
    
    return render(request, 'admin/report_filter_penjualan.html', context)


@staff_member_required
def report_filter_produk(request):
    # Logika untuk mendapatkan jenis produk choices jika perlu
    context = {'title': 'Filter Laporan Produk'}
    
    filtered_data = None
    
    if request.method == 'POST':
        # Dapatkan filter dari POST request
        jenis_produk = request.POST.get('jenis_produk')
        stok_menipis = request.POST.get('stok_menipis')
        
        # Lakukan filtering pada model Produk
        queryset = Produk.objects.all()
        
        if jenis_produk:
            queryset = queryset.filter(jenisProduk=jenis_produk)
        if stok_menipis:
            queryset = queryset.filter(stok__lt=10)  # Assuming 10 as threshold for low stock
            
        filtered_data = queryset.order_by('namaProduk')
        
        # Kirim filter yang sudah disubmit kembali ke template untuk mempertahankan nilai form
        context['submitted_filters'] = request.POST
        context['filtered_data'] = filtered_data
    
    return render(request, 'admin/report_filter_produk.html', context)


@staff_member_required
def report_filter_produksi(request):
    # Logika untuk mendapatkan jenis hasil choices (dari model Produksi) jika perlu
    context = {'title': 'Filter Laporan Produksi'}
    
    filtered_data = None
    
    if request.method == 'POST':
        # Dapatkan filter dari POST request
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        jenis_hasil = request.POST.get('jenis_hasil')
        
        # Lakukan filtering pada model Produksi
        queryset = Produksi.objects.all()
        
        if date_from:
            queryset = queryset.filter(tanggalProduksi__gte=date_from)
        if date_to:
            queryset = queryset.filter(tanggalProduksi__lte=date_to)
        if jenis_hasil:
            queryset = queryset.filter(jenisHasil=jenis_hasil)
            
        # PENTING: Gunakan prefetch_related untuk efisiensi
        queryset = queryset.select_related('idKaryawan').prefetch_related(
            'detailproduksi_set__idProduk'  # Sesuaikan dengan related_name yang benar
        ).order_by('-tanggalProduksi')

        # Lakukan perhitungan di Python untuk menambah atribut baru
        produksi_list = list(queryset)
        for produksi in produksi_list:
            total_biaya = 0
            bahan_summary_list = []
            
            # Looping melalui semua detail produksi yang terkait
            for detail in produksi.detailproduksi_set.all():
                if detail.idProduk.jenisProduk == 'Bahan Baku':
                    # 1. Kalkulasi Biaya
                    biaya_detail = detail.jumlahBahanTerpakai * detail.idProduk.harga
                    total_biaya += biaya_detail
                    
                    # 2. Buat Ringkasan Fisik Bahan
                    summary = f"{detail.jumlahBahanTerpakai} {detail.idProduk.satuan} {detail.idProduk.namaProduk}"
                    bahan_summary_list.append(summary)

            # Tambahkan atribut baru ke objek Produksi
            produksi.total_biaya_bahan = total_biaya 
            produksi.bahan_terpakai_summary = " + ".join(bahan_summary_list) if bahan_summary_list else "Tidak ada data bahan"
            
        filtered_data = produksi_list
        
        # Kirim filter yang sudah disubmit kembali ke template untuk mempertahankan nilai form
        context['submitted_filters'] = request.POST
        context['filtered_data'] = filtered_data
    
    return render(request, 'admin/report_filter_produksi.html', context)


# Report functions
def report_penjualan_pdf(request):
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("ReportLab is not installed. Please install it to generate PDF reports.")
    
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    
    # Build query
    pemesanan_list = Pemesanan.objects.all()
    
    if date_from:
        pemesanan_list = pemesanan_list.filter(tanggalPemesanan__gte=date_from)
    if date_to:
        pemesanan_list = pemesanan_list.filter(tanggalPemesanan__lte=date_to)
    if status:
        pemesanan_list = pemesanan_list.filter(status=status)
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laporan_penjualan.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("Laporan Penjualan", title_style))
    story.append(Spacer(1, 12))
    
    # Filter information
    filter_text = "Filter: "
    if date_from and date_to:
        filter_text += f"Tanggal {date_from} sampai {date_to}"
    elif date_from:
        filter_text += f"Tanggal mulai dari {date_from}"
    elif date_to:
        filter_text += f"Tanggal sampai {date_to}"
    else:
        filter_text += "Semua tanggal"
    
    if status:
        filter_text += f", Status: {status}"
    
    story.append(Paragraph(filter_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Table data
    data = [['ID', 'Tanggal', 'Pelanggan', 'Status', 'Total']]
    
    for pemesanan in pemesanan_list:
        data.append([
            str(pemesanan.idPemesanan),
            pemesanan.tanggalPemesanan.strftime('%d/%m/%Y'),
            pemesanan.idPelanggan.namaPelanggan,
            pemesanan.status,
            f"Rp {pemesanan.totalPemesanan:,}"
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    return response


def report_produk_pdf(request):
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("ReportLab is not installed. Please install it to generate PDF reports.")
    
    # Get filter parameters
    jenis_produk = request.GET.get('jenis_produk')
    stok_menipis = request.GET.get('stok_menipis')
    
    # Build query
    produk_list = Produk.objects.all()
    
    if jenis_produk:
        produk_list = produk_list.filter(jenisProduk=jenis_produk)
    
    if stok_menipis:
        produk_list = produk_list.filter(stok__lt=10)  # Assuming 10 as threshold for low stock
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laporan_produk.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("Laporan Produk", title_style))
    story.append(Spacer(1, 12))
    
    # Filter information
    filter_text = "Filter: "
    if jenis_produk:
        filter_text += f"Jenis Produk: {jenis_produk}"
    else:
        filter_text += "Semua jenis produk"
    
    if stok_menipis:
        filter_text += ", Stok Menipis: Ya"
    
    story.append(Paragraph(filter_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Table data
    data = [['Nama Produk', 'Jenis', 'Harga', 'Stok', 'Satuan']]
    
    for produk in produk_list:
        data.append([
            produk.namaProduk,
            produk.jenisProduk,
            f"Rp {produk.harga:,}",
            str(produk.stok),
            produk.satuan
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    return response


def report_produksi_pdf(request):
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("ReportLab is not installed. Please install it to generate PDF reports.")
    
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    jenis_hasil = request.GET.get('jenis_hasil')
    
    # Build query
    produksi_list = Produksi.objects.all()
    
    if date_from:
        produksi_list = produksi_list.filter(tanggalProduksi__gte=date_from)
    if date_to:
        produksi_list = produksi_list.filter(tanggalProduksi__lte=date_to)
    if jenis_hasil:
        produksi_list = produksi_list.filter(jenisHasil=jenis_hasil)
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laporan_produksi.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("Laporan Produksi", title_style))
    story.append(Spacer(1, 12))
    
    # Filter information
    filter_text = "Filter: "
    if date_from and date_to:
        filter_text += f"Tanggal {date_from} sampai {date_to}"
    elif date_from:
        filter_text += f"Tanggal mulai dari {date_from}"
    elif date_to:
        filter_text += f"Tanggal sampai {date_to}"
    else:
        filter_text += "Semua tanggal"
    
    if jenis_hasil:
        filter_text += f", Jenis Hasil: {jenis_hasil}"
    
    story.append(Paragraph(filter_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Table data
    data = [['ID', 'Tanggal Produksi', 'Jenis Hasil', 'Jumlah Hasil', 'Karyawan']]
    
    for produksi in produksi_list:
        data.append([
            str(produksi.idProduksi),
            produksi.tanggalProduksi.strftime('%d/%m/%Y'),
            produksi.jenisHasil,
            str(produksi.jumlahHasil),
            produksi.idKaryawan.nama
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    return response


# Dashboard context function
def admin_dashboard_context():
    # Calculate metrics
    total_produk_jadi = Produk.objects.filter(jenisProduk='Produk Jadi').aggregate(
        total_stok=Sum('stok')
    )['total_stok'] or 0
    
    total_pelanggan = Pelanggan.objects.count()
    
    total_pemesanan = Pemesanan.objects.count()
    
    # Calculate total revenue only from completed orders
    total_pendapatan = Pemesanan.objects.filter(status='Selesai').aggregate(
        total=Sum('totalPemesanan')
    )['total'] or 0
    
    # 1. Hitung Pesanan yang Membutuhkan Perhatian:
    # Status yang dihitung: 'Diproses' dan 'Dikirim'
    ATTENTION_STATUSES = ['Diproses', 'Dikirim']
    pesanan_perhatian_count = Pemesanan.objects.filter(status__in=ATTENTION_STATUSES).count()
    
    # 2.1 Logika Stok Menipis
    STOK_AMAN_THRESHOLD = 10 
    produk_stok_menipis = Produk.objects.filter(stok__lt=STOK_AMAN_THRESHOLD).order_by('namaProduk')
    
    # Calculate monthly revenue for the last 6 months (only completed orders)
    today = timezone.now().date()
    monthly_revenue = []
    labels = []
    
    for i in range(5, -1, -1):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        revenue = Pemesanan.objects.filter(
            tanggalPemesanan__gte=month_start,
            tanggalPemesanan__lte=month_end,
            status='Selesai'
        ).aggregate(total=Sum('totalPemesanan'))['total'] or 0
        
        monthly_revenue.append(int(revenue))
        labels.append(month_start.strftime('%B %Y'))
    
    context = {
        'total_produk_jadi': total_produk_jadi,
        'total_pelanggan': total_pelanggan,
        'total_pemesanan': total_pemesanan,
        'total_pendapatan': total_pendapatan,
        'monthly_revenue': monthly_revenue,
        'labels': labels,
        # 2. Tambahkan ke context (untuk card dan template index.html):
        'pesanan_perhatian_count': pesanan_perhatian_count,
        # 2.1 Logika Stok Menipis
        'produk_stok_menipis': produk_stok_menipis,
        'stok_menipis_count': produk_stok_menipis.count(),
        'stok_aman_threshold': STOK_AMAN_THRESHOLD
    }
    
    return context


# Monkey patch the AdminSite to inject our dashboard context
def custom_index(self, request, extra_context=None):
    # Get the original index method
    context = admin_dashboard_context()
    if extra_context:
        context.update(extra_context)
    return super(CustomAdminSite, self).index(request, extra_context=context)


# Apply the monkey patch
CustomAdminSite.index = custom_index


# Jazzmin Customization
def get_pesanan_perhatian_count(request):
    ATTENTION_STATUSES = ['Diproses', 'Dikirim']
    # Memastikan fungsi dapat diakses oleh Jazzmin
    return Pemesanan.objects.filter(status__in=ATTENTION_STATUSES).count()

