from django.contrib import admin
from django.db.models import Sum
from .models import Karyawan, Produk, Produksi, DetailProduksi, Pelanggan, Pembelian, DetailPembelian, Penjualan, DetailPenjualan

# Register your models here.

class DetailProduksiInline(admin.TabularInline):
    model = DetailProduksi
    extra = 1


@admin.register(Karyawan)
class KaryawanAdmin(admin.ModelAdmin):
    list_display = ('idKaryawan', 'nama', 'username')
    search_fields = ('nama', 'username')
    list_filter = ('nama',)
    ordering = ('idKaryawan',)


@admin.register(Produk)
class ProdukAdmin(admin.ModelAdmin):
    list_display = ('idProduk', 'namaProduk', 'jenisProduk', 'harga', 'stok', 'satuan')
    search_fields = ('namaProduk',)
    list_filter = ('jenisProduk',)
    ordering = ('idProduk',)


@admin.register(Produksi)
class ProduksiAdmin(admin.ModelAdmin):
    list_display = ('idProduksi', 'tanggalProduksi', 'jenisHasil', 'jumlahHasil', 'idKaryawan')
    search_fields = ('jenisHasil',)
    list_filter = ('tanggalProduksi', 'jenisHasil', 'idKaryawan')
    ordering = ('-tanggalProduksi',)
    inlines = [DetailProduksiInline]


class DetailPembelianInline(admin.TabularInline):
    model = DetailPembelian
    extra = 1


@admin.register(Pelanggan)
class PelangganAdmin(admin.ModelAdmin):
    list_display = ('idPelanggan', 'namaPelanggan', 'alamat', 'noTelp', 'username')
    search_fields = ('namaPelanggan', 'username')
    list_filter = ('namaPelanggan',)
    ordering = ('idPelanggan',)


@admin.register(Pembelian)
class PembelianAdmin(admin.ModelAdmin):
    list_display = ('idPembelian', 'tanggalPembelian', 'totalPembelian', 'idPelanggan')
    search_fields = ('idPelanggan__namaPelanggan',)
    list_filter = ('tanggalPembelian', 'idPelanggan')
    ordering = ('-tanggalPembelian',)
    readonly_fields = ('totalPembelian',)
    inlines = [DetailPembelianInline]


class DetailPenjualanInline(admin.TabularInline):
    model = DetailPenjualan
    extra = 1


@admin.register(Penjualan)
class PenjualanAdmin(admin.ModelAdmin):
    list_display = ('idPenjualan', 'tanggalPenjualan', 'totalPenjualan', 'idKaryawan', 'idPelanggan')
    search_fields = ('idPelanggan__namaPelanggan',)
    list_filter = ('tanggalPenjualan', 'idKaryawan', 'idPelanggan')
    ordering = ('-tanggalPenjualan',)
    readonly_fields = ('totalPenjualan',)
    inlines = [DetailPenjualanInline]
