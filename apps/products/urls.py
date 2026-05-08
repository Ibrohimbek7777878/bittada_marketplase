"""URL routes for `products` — Django Templates."""
from __future__ import annotations

from django.urls import path
from django.views.generic.base import RedirectView  # Eski /manage/* URL'larini /dashboard/* ga yo'naltirish uchun

from .views import (
    # Template Views
    home_view,
    category_detail_view,
    product_detail_view,
    services_view,
    manufacturers_view,
    company_view,
    cart_view,
    wishlist_view,
    login_view,
    register_view,
    profile_view,
    profile_edit_view,  # Profilni tahrirlash (alohida sahifa)
    orders_view,
    logout_view,
    seller_profile_view,
    customer_register_view,  # Mijozlar uchun alohida ro'yxatdan o'tish
    escrow_view,
    manufacturing_view,
    download_catalog,
    # Sayt admin paneli — Custom Views (ERP UI, Django admin emas)
    product_admin_list_view,  # Mahsulotlar ro'yxati (filter+pagination)
    product_admin_create_view,  # Yangi mahsulot yaratish formasi
    # API Views (optional, for AJAX)
    api_products_list,
    api_product_detail,
    api_category_tree,
)

urlpatterns: list = [
    # Template Views
    path("", home_view, name="home"),
    path("category/<slug:category_slug>/", category_detail_view, name="category_detail"),
    path("product/<str:uuid>/", product_detail_view, name="product_detail"),
    path("manufacturers/", manufacturers_view, name="manufacturers"),
    path("cart/", cart_view, name="cart"),
    path("wishlist/", wishlist_view, name="wishlist"),
    path("profile/edit/", profile_edit_view, name="profile_edit"),  # Profilni tahrirlash (alohida sahifa)
    path("profile/", profile_view, name="profile"),
    path("orders/", orders_view, name="orders"),
    path("u/<str:username>/", seller_profile_view, name="public-profile"),
    path("escrow/", escrow_view, name="escrow"),
    path("manufacturing/", manufacturing_view, name="manufacturing"),
    path("manufacturing/download/", download_catalog, name="download_catalog"),

    # ─────────────────────────────────────────────────────────────────────
    # MIGRATION SHIM (2026-05-02 v3):
    # Eski /manage/products/* yo'llari Bittada ERP ekotizimiga ko'chirildi.
    # Bu RedirectView'lar:
    #   1) Eski {% url 'admin_product_list' %} chaqiruvlari NoReverseMatch bermaydi.
    #   2) Eski bookmark/link orqali kelgan foydalanuvchini 404 emas, /dashboard/* ga olib boradi.
    # Eski view funksiyalari (product_admin_list_view, product_admin_create_view)
    # apps/products/views.py'da SAQLANIB QOLGAN (daxlsizlik qoidasi).
    # ─────────────────────────────────────────────────────────────────────
    path(
        "manage/products/",  # Eski URL
        RedirectView.as_view(url="/dashboard/products/", permanent=False),  # 302 → ERP
        name="admin_product_list",  # Eski reverse nom (template'lar uchun)
    ),
    path(
        "manage/products/create/",  # Eski URL
        RedirectView.as_view(url="/dashboard/products/", permanent=False),  # ERP list (create UI keyingi vazifada)
        name="admin_product_create",  # Eski reverse nom
    ),

    # Placeholder (bo'sh) pathlar - NoReverseMatch xatolarini oldini olish uchun

    path("masters/", home_view, name="masters"),
    path("3d-design/", home_view, name="3d-design"),
    path("support/", home_view, name="support"),
    path("company/", company_view, name="company"),
    path("courses/", home_view, name="courses"),
]
