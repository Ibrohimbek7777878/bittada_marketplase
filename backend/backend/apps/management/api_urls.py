"""
DRF API URL'lari — /dashboard/api/v1/...

DefaultRouter avtomatik tarzda quyidagi yo'llarni yaratadi:
    GET    /products/              → list
    POST   /products/              → create
    GET    /products/<pk>/         → retrieve
    PUT    /products/<pk>/         → update
    PATCH  /products/<pk>/         → partial_update
    DELETE /products/<pk>/         → destroy
    + custom @action endpointlar (kpis, blacklist, block, unblock va h.k.)

Mount nuqtasi (config/urls.py):
    path("dashboard/api/v1/", include("apps.management.api_urls"))
"""
from __future__ import annotations  # Annotatsiya kelajak

from django.urls import include, path  # URL helperlari
from rest_framework.routers import DefaultRouter  # Avtomatik routing

from .api.viewsets import (
    ManagementCreditViewSet,
    ManagementEscrowViewSet,
    ManagementOrderViewSet,
    ManagementProductViewSet,
    ManagementUserViewSet,
)

# ─────────────────────────────────────────────────────────────────────────────
# Router — har bir ViewSet uchun avtomatik URL'lar yaratadi
# ─────────────────────────────────────────────────────────────────────────────
router = DefaultRouter()  # DRF standart router

# Mahsulotlar — to'liq CRUD
router.register(r"products", ManagementProductViewSet, basename="mgmt-products")

# Buyurtmalar — list/retrieve/update (create yo'q, chunki saytdan keladi)
router.register(r"orders", ManagementOrderViewSet, basename="mgmt-orders")

# Escrow — read-only (list/retrieve)
router.register(r"escrow", ManagementEscrowViewSet, basename="mgmt-escrow")

# Foydalanuvchilar — list/retrieve/update + block/unblock actions
router.register(r"users", ManagementUserViewSet, basename="mgmt-users")

# Credit — viewsets.ViewSet (custom, faqat list)
router.register(r"credit", ManagementCreditViewSet, basename="mgmt-credit")


# ─────────────────────────────────────────────────────────────────────────────
# urlpatterns — config/urls.py shu ro'yxatni include qiladi
# ─────────────────────────────────────────────────────────────────────────────
urlpatterns = [
    path("", include(router.urls)),  # Router'dagi barcha yo'llarni qo'shish
]
