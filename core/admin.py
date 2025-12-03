from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Karyawan, Produk, Produksi, DetailProduksi, Pelanggan, Pembelian, DetailPembelian, Penjualan, DetailPenjualan


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
    list_display = ('idKaryawan', 'nama', 'username', 'action_buttons')
    search_fields = ('nama', 'username')
    list_filter = ('nama',)
    ordering = ('idKaryawan',)
    
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-primary btn-sm" href="/admin/core/karyawan/{}/change/">Edit</a>&nbsp;'
            '<a class="btn btn-danger btn-sm" href="/admin/core/karyawan/{}/delete/">Delete</a>',
            obj.pk, obj.pk
        )
    action_buttons.short_description = 'Actions'


@admin.register(Produk, site=custom_admin_site)
class ProdukAdmin(admin.ModelAdmin):
    list_display = ('idProduk', 'namaProduk', 'jenisProduk', 'harga', 'stok', 'satuan', 'action_buttons')
    search_fields = ('namaProduk',)
    list_filter = ('jenisProduk',)
    ordering = ('idProduk',)
    
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-primary btn-sm" href="/admin/core/produk/{}/change/">Edit</a>&nbsp;'
            '<a class="btn btn-danger btn-sm" href="/admin/core/produk/{}/delete/">Delete</a>',
            obj.pk, obj.pk
        )
    action_buttons.short_description = 'Actions'


@admin.register(Produksi, site=custom_admin_site)
class ProduksiAdmin(admin.ModelAdmin):
    list_display = ('idProduksi', 'tanggalProduksi', 'jenisHasil', 'jumlahHasil', 'idKaryawan', 'action_buttons')
    search_fields = ('jenisHasil',)
    list_filter = ('tanggalProduksi', 'jenisHasil', 'idKaryawan')
    ordering = ('-tanggalProduksi',)
    inlines = [DetailProduksiInline]
    
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-primary btn-sm" href="/admin/core/produksi/{}/change/">Edit</a>&nbsp;'
            '<a class="btn btn-danger btn-sm" href="/admin/core/produksi/{}/delete/">Delete</a>',
            obj.pk, obj.pk
        )
    action_buttons.short_description = 'Actions'


class DetailPembelianInline(admin.TabularInline):
    model = DetailPembelian
    extra = 1
    readonly_fields = ('subTotal',)


@admin.register(Pelanggan, site=custom_admin_site)
class PelangganAdmin(admin.ModelAdmin):
    list_display = ('idPelanggan', 'namaPelanggan', 'alamat', 'noTelp', 'username', 'action_buttons')
    search_fields = ('namaPelanggan', 'username')
    list_filter = ('namaPelanggan',)
    ordering = ('idPelanggan',)
    
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-primary btn-sm" href="/admin/core/pelanggan/{}/change/">Edit</a>&nbsp;'
            '<a class="btn btn-danger btn-sm" href="/admin/core/pelanggan/{}/delete/">Delete</a>',
            obj.pk, obj.pk
        )
    action_buttons.short_description = 'Actions'


@admin.register(Pembelian, site=custom_admin_site)
class PembelianAdmin(admin.ModelAdmin):
    list_display = ('idPembelian', 'tanggalPembelian', 'totalPembelian', 'idPelanggan', 'action_buttons')
    search_fields = ('idPelanggan__namaPelanggan',)
    list_filter = ('tanggalPembelian', 'idPelanggan')
    ordering = ('-tanggalPembelian',)
    readonly_fields = ('totalPembelian',)
    inlines = [DetailPembelianInline]
    
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-primary btn-sm" href="/admin/core/pembelian/{}/change/">Edit</a>&nbsp;'
            '<a class="btn btn-danger btn-sm" href="/admin/core/pembelian/{}/delete/">Delete</a>',
            obj.pk, obj.pk
        )
    action_buttons.short_description = 'Actions'
    
    def save_formset(self, request, form, formset, change):
        # Save the formset first
        formset.save()
        
        # Calculate total from details
        total = formset.instance.detailpembelian_set.aggregate(
            total=Sum('subTotal')
        )['total'] or 0
        
        # Update the parent object
        formset.instance.totalPembelian = total
        formset.instance.save()


class DetailPenjualanInline(admin.TabularInline):
    model = DetailPenjualan
    extra = 1
    readonly_fields = ('subTotal',)


@admin.register(Penjualan, site=custom_admin_site)
class PenjualanAdmin(admin.ModelAdmin):
    list_display = ('idPenjualan', 'tanggalPenjualan', 'totalPenjualan', 'idKaryawan', 'idPelanggan', 'action_buttons')
    search_fields = ('idPelanggan__namaPelanggan',)
    list_filter = ('tanggalPenjualan', 'idKaryawan', 'idPelanggan')
    ordering = ('-tanggalPenjualan',)
    readonly_fields = ('totalPenjualan',)
    inlines = [DetailPenjualanInline]
    
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-primary btn-sm" href="/admin/core/penjualan/{}/change/">Edit</a>&nbsp;'
            '<a class="btn btn-danger btn-sm" href="/admin/core/penjualan/{}/delete/">Delete</a>',
            obj.pk, obj.pk
        )
    action_buttons.short_description = 'Actions'
    
    def save_formset(self, request, form, formset, change):
        # Save the formset first
        formset.save()
        
        # Calculate total from details
        total = formset.instance.detailpenjualan_set.aggregate(
            total=Sum('subTotal')
        )['total'] or 0
        
        # Update the parent object
        formset.instance.totalPenjualan = total
        formset.instance.save()


# Dashboard context function
def admin_dashboard_context():
    # Calculate metrics
    total_produk_jadi = Produk.objects.filter(jenisProduk='Produk Jadi').aggregate(
        total_stok=Sum('stok')
    )['total_stok'] or 0
    
    total_pelanggan = Pelanggan.objects.count()
    
    total_pembelian = Pembelian.objects.count()
    
    total_pendapatan = Penjualan.objects.aggregate(
        total=Sum('totalPenjualan')
    )['total'] or 0
    
    # Calculate monthly revenue for the last 6 months
    today = timezone.now().date()
    monthly_revenue = []
    labels = []
    
    for i in range(5, -1, -1):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        revenue = Penjualan.objects.filter(
            tanggalPenjualan__gte=month_start,
            tanggalPenjualan__lte=month_end
        ).aggregate(total=Sum('totalPenjualan'))['total'] or 0
        
        monthly_revenue.append(int(revenue))
        labels.append(month_start.strftime('%B %Y'))
    
    context = {
        'total_produk_jadi': total_produk_jadi,
        'total_pelanggan': total_pelanggan,
        'total_pembelian': total_pembelian,
        'total_pendapatan': total_pendapatan,
        'monthly_revenue': monthly_revenue,
        'labels': labels,
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