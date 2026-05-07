from __future__ import annotations

from django.urls import path

from .views import (
    api_products_list,
    api_product_detail,
    api_category_tree,
)
from .cart_views import api_cart_count

app_name = "products_api"

urlpatterns: list = [
    path("", api_products_list, name="list"),
    path("<str:uuid>/", api_product_detail, name="detail"),
    path("categories/tree/", api_category_tree, name="categories-tree"),
    path("cart/count/", api_cart_count, name="cart-count"),
]
