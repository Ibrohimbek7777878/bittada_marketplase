"""URL routes for `orders`. Mounted under `/api/v1/orders/`.

Daxlsizlik eslatma: mavjud `urlpatterns` (DRF API) o'zgarmagan. Faylning
oxiriga yangi `seller_order_urlpatterns` qo'shildi — u `config/urls.py`
orqali `/dashboard/seller/orders/` prefiksiga ulanadi (seller namespace).
"""
from __future__ import annotations

from django.urls import path

from apps.orders import views

app_name = "orders"

urlpatterns: list = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("list/", views.OrderListView.as_view(), name="list"),
]


# === YANGI: Seller dashboard'dagi buyurtma URL'lari ===
# Bu ro'yxat config/urls.py'da `dashboard/seller/orders/` prefiksiga
# ulanadi. Namespace: "seller" (apps/products/urls.py'dagi
# `seller_dashboard_urlpatterns` bilan birlashtiriladi).
seller_order_urlpatterns = [
    # Ro'yxat: /dashboard/seller/orders/  →  name="seller:orders_list"
    path("orders/", views.SellerOrderListView.as_view(), name="orders_list"),
    # Detali: /dashboard/seller/orders/<uuid:pk>/  →  name="seller:order_detail"
    path("orders/<uuid:pk>/", views.SellerOrderDetailView.as_view(), name="order_detail"),
]
