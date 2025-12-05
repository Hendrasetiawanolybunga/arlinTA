"""
URL configuration for arlinSkripsi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from core.admin import custom_admin_site
# Import views for root URL
from core import views_pelanggan
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Root path -> Customer login
    path('', views_pelanggan.pelanggan_login, name='root_login'),
    
    # Admin Interface
    path('admin/', custom_admin_site.urls),
    
    # All Customer URLs (concise)
    # Using empty path so URLs in core/urls_pelanggan.py become /login/, /beranda/, etc.
    path('', include('core.urls_pelanggan')),
    
    # Core/Admin/Report URLs (under /core/)
    path('core/', include('core.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)