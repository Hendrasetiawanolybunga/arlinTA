from django.urls import path
from . import views_pelanggan

urlpatterns = [
    # Authentication
    path('register/', views_pelanggan.pelanggan_register, name='pelanggan_register'),
    path('login/', views_pelanggan.pelanggan_login, name='pelanggan_login'),
    path('logout/', views_pelanggan.pelanggan_logout, name='pelanggan_logout'),
    
    # Dashboard/Home
    path('beranda/', views_pelanggan.pelanggan_beranda, name='pelanggan_beranda'),
    
    # Products
    path('produk/', views_pelanggan.pelanggan_produk_list, name='pelanggan_produk_list'),
    
    # Cart
    path('keranjang/', views_pelanggan.pelanggan_keranjang_view, name='pelanggan_keranjang_view'),
    path('keranjang/add/', views_pelanggan.pelanggan_keranjang_add, name='pelanggan_keranjang_add'),
    path('keranjang/update/', views_pelanggan.pelanggan_keranjang_update, name='pelanggan_keranjang_update'),
    path('keranjang/delete/', views_pelanggan.pelanggan_keranjang_delete, name='pelanggan_keranjang_delete'),
    
    # Checkout
    path('checkout/', views_pelanggan.pelanggan_checkout, name='pelanggan_checkout'),
    path('checkout/view/', views_pelanggan.pelanggan_checkout_view, name='pelanggan_checkout_view'),
    
    # Orders
    path('pesanan/riwayat/', views_pelanggan.pelanggan_pesanan_riwayat, name='pelanggan_pesanan_riwayat'),
    path('pesanan/detail/<int:pesanan_id>/', views_pelanggan.pelanggan_pesanan_detail_html, name='pelanggan_pesanan_detail_html'),
    
    # Account
    path('akun/', views_pelanggan.pelanggan_akun, name='pelanggan_akun'),
]