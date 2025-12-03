from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from .models import Produk, Pelanggan, Pemesanan
from .admin import admin_dashboard_context


@staff_member_required
def admin_dashboard(request):
    # Get dashboard context data
    context = admin_dashboard_context()
    return render(request, 'admin/index.html', context)