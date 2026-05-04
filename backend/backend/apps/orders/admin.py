"""Django admin registrations for `orders`."""
from __future__ import annotations

from django.contrib import admin  # noqa: F401

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'seller', 'status', 'total_price', 'escrow_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__username', 'seller__username', 'id']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
