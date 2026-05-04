"""URL routes for `orders`. Mounted under `/api/v1/orders/`."""
from __future__ import annotations

from django.urls import path

from apps.orders import views

app_name = "orders"

urlpatterns: list = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("list/", views.OrderListView.as_view(), name="list"),
]
