"""URL routes for `products` — Django Templates.

Daxlsizlik eslatma: bu fayl mavjud `urlpatterns` ro'yxatini saqlaydi.
Faqat oxiriga yangi `seller_dashboard_urlpatterns` ro'yxati qo'shildi —
u `config/urls.py` orqali `/dashboard/seller/` prefix'ga ulanadi.
"""
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
    # === YANGI: Seller dashboard CBV'lari (/dashboard/seller/...) ===
    SellerDashboardIndexView,  # Umumiy panel (bosh sahifa)
    SellerProductListView,  # Mahsulotlar ro'yxati
    SellerProductCreateView,  # Yangi mahsulot qo'shish
    SellerProductUpdateView,  # Mahsulotni tahrirlash
    # API Views (optional, for AJAX)
    api_products_list,
    api_product_detail,
    api_category_tree,
)
# SellerProfileEditView users app'da — apps/users/views.py'dan import qilamiz
# (loyiha tuzilishi: profile-mantig'i users app'da bo'lishi mantiqan to'g'ri)
from apps.users.views import SellerProfileEditView  # noqa: E402

urlpatterns: list = [
    # Template Views
    path("", home_view, name="home"),
    path("select-role/", login_view, name="select-role"),  # Role selection page before register
    path("category/<slug:category_slug>/", category_detail_view, name="category_detail"),
    path("product/<uuid:uuid>/", product_detail_view, name="product_detail"),
    path("services/", services_view, name="services"),
    path("manufacturers/", manufacturers_view, name="manufacturers"),
    path("cart/", cart_view, name="cart"),
    path("wishlist/", wishlist_view, name="wishlist"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("register/customer/", customer_register_view, name="customer-register"),  # Mijoz uchun soddalashtirilgan ro'yxatdan o'tish
    path("profile/edit/", profile_edit_view, name="profile_edit"),  # Profilni tahrirlash (alohida sahifa)
    path("profile/", profile_view, name="profile"),
    path("orders/", orders_view, name="orders"),
    path("logout/", logout_view, name="logout"),
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


# ============================================================================
# YANGI: Seller dashboard URL'lari — /dashboard/seller/...
# ────────────────────────────────────────────────────────────────────────────
# Bu ro'yxat `config/urls.py`'da `path("dashboard/seller/", include(...))`
# orqali ulanadi (management dan oldin, chunki Django top-down match qiladi).
# Namespace: "seller" — templatelar ichida `{% url 'seller:products_list' %}`.
# ============================================================================
seller_dashboard_urlpatterns = [
    # Bosh sahifa: /dashboard/seller/  → umumiy panel (statistika)
    path("", SellerDashboardIndexView.as_view(), name="dashboard"),

    # Mahsulotlar bo'limi
    # /dashboard/seller/products/  → ro'yxat
    path("products/", SellerProductListView.as_view(), name="products_list"),
    # /dashboard/seller/products/add/  → yangi qo'shish
    path("products/add/", SellerProductCreateView.as_view(), name="product_create"),
    # /dashboard/seller/products/<uuid>/edit/  → tahrirlash
    # Product modeli pk = UUID — converter "uuid" ishlatamiz
    path("products/<uuid:pk>/edit/", SellerProductUpdateView.as_view(), name="product_edit"),

    # Profil tahrirlash (apps/users/views.py'dagi SellerProfileEditView)
    # /dashboard/seller/profile/edit/
    path("profile/edit/", SellerProfileEditView.as_view(), name="profile_edit"),
]
