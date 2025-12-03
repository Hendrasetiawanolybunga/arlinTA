from django.urls import path
from . import views
from core.admin import (
    report_penjualan_pdf, 
    report_produk_pdf, 
    report_produksi_pdf,
    report_filter_penjualan,
    report_filter_produk,
    report_filter_produksi
)

app_name = 'core'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # Halaman Filter (View baru)
    path('admin/filter/penjualan/', report_filter_penjualan, name='filter_penjualan'),
    path('admin/filter/produk/', report_filter_produk, name='filter_produk'),
    path('admin/filter/produksi/', report_filter_produksi, name='filter_produksi'),
    # URL PDF (Target Form Submission)
    path('admin/report/penjualan/pdf/', report_penjualan_pdf, name='report_penjualan_pdf'),
    path('admin/report/produk/pdf/', report_produk_pdf, name='report_produk_pdf'),
    path('admin/report/produksi/pdf/', report_produksi_pdf, name='report_produksi_pdf'),
    
    # Karyawan URLs
    path('karyawan/login/', views.karyawan_login, name='karyawan_login'),
    path('karyawan/logout/', views.karyawan_logout, name='karyawan_logout'),
    path('karyawan/dashboard/', views.karyawan_dashboard, name='karyawan_dashboard'),
    path('karyawan/produksi/input/', views.karyawan_produksi_input, name='karyawan_produksi_input'),
]