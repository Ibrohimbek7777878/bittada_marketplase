"""
URL'lar (HTML sahifalar) — apps.management.

Bu module faqat HTML sahifalar uchun (sidebar tugmalari).
DRF API endpointlari alohida — apps.management.api_urls'da.

Mount nuqtasi (config/urls.py):
    path("dashboard/", include(("apps.management.urls", "management"), namespace="mgmt"))

Demak template'larda:
    {% url 'mgmt:products_list' %}  → /dashboard/products/
    {% url 'mgmt:orders_list' %}    → /dashboard/orders/
    {% url 'mgmt:escrow_list' %}    → /dashboard/escrow/
    {% url 'mgmt:credit_list' %}    → /dashboard/credit/
    {% url 'mgmt:users_list' %}     → /dashboard/users/
    {% url 'mgmt:blacklist' %}      → /dashboard/users/blacklist/
"""
from __future__ import annotations  # Annotatsiya kelajak rejimi

from django.urls import path  # URL routing helper

from . import views  # HTML view'lar shu yerda

app_name = "management"  # Namespace nomi (template'larda "mgmt:" ishlatamiz config'da)

urlpatterns = [  # ERP HTML sahifalari
    # Bosh sahifa (Mahsulotlar bo'limiga redirect — default landing)
    path("", views.dashboard_index, name="index"),  # /dashboard/

    # Mahsulotlar
    path("products/", views.products_list_view, name="products_list"),  # /dashboard/products/

    # Savdo (Sales)
    path("orders/", views.orders_list_view, name="orders_list"),  # /dashboard/orders/

    # Escrow Fund
    path("escrow/", views.escrow_list_view, name="escrow_list"),  # /dashboard/escrow/

    # Credit Economy
    path("credit/", views.credit_list_view, name="credit_list"),  # /dashboard/credit/

    # Foydalanuvchilar (faqat admin)
    path("users/", views.users_list_view, name="users_list"),  # /dashboard/users/

    # Qora ro'yxat (faqat admin) — alohida path
    path("users/blacklist/", views.blacklist_view, name="blacklist"),  # /dashboard/users/blacklist/
]
