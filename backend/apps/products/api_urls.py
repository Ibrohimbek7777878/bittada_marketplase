from __future__ import annotations

from django.urls import path

from .views import (
    api_products_list,
    api_product_detail,
    api_category_tree,
    ProductReviewListCreateAPIView,
    ProductReviewDetailAPIView,
)

app_name = "products_api"

urlpatterns: list = [
    path("", api_products_list, name="list"),
    path("<str:uuid>/", api_product_detail, name="detail"),
    path("<str:uuid>/reviews/", ProductReviewListCreateAPIView.as_view(), name="product-reviews"),
    path("reviews/<int:id>/", ProductReviewDetailAPIView.as_view(), name="review-detail"),
    path("categories/tree/", api_category_tree, name="categories-tree"),
]
