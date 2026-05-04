"""
DRF ViewSets — Bittada ERP boshqaruv API.

Har bir ViewSet:
    - permission_classes orqali himoyalanadi (IsManagementUser yoki IsManagementAdmin)
    - filterlash, qidiruv, saralash imkoniyatlariga ega
    - selectors.py orqali ma'lumot oladi (rolga muvofiq)
    - services.py orqali yozadi (transactional)

URL'lar (DefaultRouter): apps/management/api_urls.py'da.

Frontend bu API'larni quyidagi yo'llardan chaqiradi:
    GET  /dashboard/api/v1/products/       → mahsulotlar ro'yxati
    POST /dashboard/api/v1/products/       → yangi mahsulot
    GET  /dashboard/api/v1/products/<id>/  → bitta mahsulot
    ...va h.k. (Orders, Escrow, Users, Credit)
"""
from __future__ import annotations  # Annotatsiya kelajak

from rest_framework import filters, mixins, status, viewsets  # DRF asosiy modullar
from rest_framework.decorators import action  # Custom endpointlar uchun
from rest_framework.response import Response  # JSON javob

from apps.orders.models import Order  # Savdo modeli
from apps.products.models import Product  # Mahsulot modeli

from .. import selectors, services  # Ichki business mantiq
from ..permissions import IsManagementAdmin, IsManagementUser  # Custom permissionlar
from .serializers import (
    ManagementOrderSerializer,
    ManagementProductSerializer,
    ManagementUserSerializer,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. PRODUCTS — Mahsulotlar boshqaruvi
# ─────────────────────────────────────────────────────────────────────────────

class ManagementProductViewSet(viewsets.ModelViewSet):
    """Mahsulotlarni boshqarish CRUD API.

    URL prefix: /dashboard/api/v1/products/
    Endpointlar:
        GET    /              → list (filterlanadi: rolga ko'ra)
        POST   /              → yangi yaratish (seller=request.user avtomatik)
        GET    /<pk>/         → bitta mahsulot
        PUT    /<pk>/         → to'liq yangilash
        PATCH  /<pk>/         → qisman yangilash
        DELETE /<pk>/         → o'chirish
        GET    /kpis/         → custom action: KPI raqamlar (stat-card uchun)
    """

    serializer_class = ManagementProductSerializer  # JSON formati
    permission_classes = [IsManagementUser]  # Faqat ERP foydalanuvchilari
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # Qidiruv + saralash
    search_fields = ["title_uz", "sku", "hashtags"]  # ?search=... uchun maydonlar
    ordering_fields = ["created_at", "price", "view_count", "stock_qty"]  # ?ordering=... uchun
    ordering = ["-created_at"]  # Default: yangilari yuqorida

    def get_queryset(self):  # noqa: D401 — DRF override
        """Rolga ko'ra filterlangan QuerySet (selectors.py'dan)."""
        return selectors.list_products_for_management(self.request.user)  # Sotuvchi → o'zinikilar

    def perform_create(self, serializer):
        """Yangi mahsulot yaratishda seller'ni avtomatik biriktirish."""
        # Service qatlami orqali — daxlsizlik va kelajakdagi audit/event uchun
        product = services.create_product_for_seller(
            seller=self.request.user,  # request.user avtomatik
            payload=serializer.validated_data,  # Validatsiyadan o'tgan ma'lumot
        )
        # Serializerga yangi yaratilgan obyektni biriktirish
        serializer.instance = product

    @action(detail=False, methods=["get"], url_path="kpis")  # /products/kpis/
    def kpis(self, request):
        """KPI raqamlari — sahifa yuqorisidagi 3 ta stat-card uchun."""
        return Response(selectors.get_product_kpis())  # JSON: {total, published, draft}


# ─────────────────────────────────────────────────────────────────────────────
# 2. ORDERS — Savdo (Sales)
# ─────────────────────────────────────────────────────────────────────────────

class ManagementOrderViewSet(
    mixins.ListModelMixin,  # GET /
    mixins.RetrieveModelMixin,  # GET /<pk>/
    mixins.UpdateModelMixin,  # PUT/PATCH /<pk>/ — status o'zgartirish uchun
    viewsets.GenericViewSet,
):
    """Buyurtmalarni boshqarish (CRUD'dan create/delete'siz).

    Yangi buyurtma yaratish saytdan (apps.orders.views) bo'ladi —
    bu erda admin faqat ko'radi va statusni boshqaradi.
    """

    serializer_class = ManagementOrderSerializer
    permission_classes = [IsManagementUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["customer__username", "seller__username", "shipping_address"]
    ordering_fields = ["created_at", "total_price", "status"]
    ordering = ["-created_at"]  # Yangilari yuqorida

    def get_queryset(self):
        """Rolga ko'ra filterlangan buyurtmalar."""
        return selectors.list_orders_for_management(self.request.user)

    @action(detail=False, methods=["get"], url_path="kpis")  # /orders/kpis/
    def kpis(self, request):
        """Savdo KPI: total/active/new/completed/gmv."""
        return Response(selectors.get_sales_kpis())


# ─────────────────────────────────────────────────────────────────────────────
# 3. ESCROW — Pul ushlangan buyurtmalar (Order modeli ustida)
# ─────────────────────────────────────────────────────────────────────────────

class ManagementEscrowViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Escrow Fund — read-only ko'rinish (faqat list/detail).

    Pul harakati Order'ning status o'zgarishi orqali sodir bo'ladi
    (apps.escrow.services kelajakda — shu yerdan emas).
    """

    serializer_class = ManagementOrderSerializer  # Order ustida ishlaydi
    permission_classes = [IsManagementUser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "escrow_amount"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Faqat escrow'da pul ushlangan buyurtmalar."""
        return selectors.list_escrow_orders(self.request.user)

    @action(detail=False, methods=["get"], url_path="kpis")  # /escrow/kpis/
    def kpis(self, request):
        """Escrow KPI: jami muzlatilgan/pending/disputed."""
        return Response(selectors.get_escrow_kpis())


# ─────────────────────────────────────────────────────────────────────────────
# 4. USERS — Foydalanuvchilar boshqaruvi (faqat admin)
# ─────────────────────────────────────────────────────────────────────────────

class ManagementUserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,  # is_active ni o'zgartirish (block/unblock)
    viewsets.GenericViewSet,
):
    """Foydalanuvchilarni boshqarish — faqat admin/super_admin/staff."""

    serializer_class = ManagementUserSerializer
    permission_classes = [IsManagementAdmin]  # Seller bu yerga kira olmaydi
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "phone"]
    ordering_fields = ["created_at", "username"]  # User modeli BaseModel'dan keladi → created_at
    ordering = ["-created_at"]

    def get_queryset(self):
        """Barcha foydalanuvchilar (selector orqali)."""
        return selectors.list_users_for_management()

    @action(detail=True, methods=["post"], url_path="block")  # POST /users/<id>/block/
    def block(self, request, pk=None):
        """Foydalanuvchini bloklash (is_active=False)."""
        user = self.get_object()  # 404 avtomatik
        services.block_user(user=user)  # Service qatlami orqali
        return Response({"detail": "Foydalanuvchi bloklandi.", "is_active": False})

    @action(detail=True, methods=["post"], url_path="unblock")  # POST /users/<id>/unblock/
    def unblock(self, request, pk=None):
        """Foydalanuvchini bloklikdan chiqarish (is_active=True)."""
        user = self.get_object()
        services.unblock_user(user=user)
        return Response({"detail": "Foydalanuvchi bloklikdan chiqarildi.", "is_active": True})

    @action(detail=False, methods=["get"], url_path="kpis")  # /users/kpis/
    def kpis(self, request):
        """Foydalanuvchilar KPI: total/customers/sellers/blacklisted."""
        return Response(selectors.get_users_kpis())

    @action(detail=False, methods=["get"], url_path="blacklist")  # /users/blacklist/
    def blacklist(self, request):
        """Qora ro'yxat (is_active=False) — alohida ro'yxat."""
        queryset = selectors.list_blacklist_users()  # Faqat bloklanganlar
        # Manual paginatsiya (DRF DefaultPagination ham ishlatish mumkin)
        page = self.paginate_queryset(queryset)  # Agar pagination mavjud bo'lsa
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)  # Pagination yo'q bo'lsa
        return Response(serializer.data)


# ─────────────────────────────────────────────────────────────────────────────
# 5. CREDIT — Bittada Credit Economy (placeholder)
# ─────────────────────────────────────────────────────────────────────────────

class ManagementCreditViewSet(viewsets.ViewSet):
    """Credit Economy — hozircha faqat KPI endpointi.

    To'liq CRUD apps.billing modeli to'liq amalga oshganda qo'shiladi
    (TZ §15 — keyingi vazifalar).
    """

    permission_classes = [IsManagementUser]  # Sotuvchi ham o'zining credit'ini ko'radi

    def list(self, request):
        """GET /credit/ — Credit Economy haqida umumiy ma'lumot."""
        return Response({  # Hozircha KPI bilan birga
            "kpis": selectors.get_credit_kpis(),
            "transactions": [],  # Placeholder: kelajakda CreditTransaction.objects.filter(...)
            "note": "Credit Economy to'liq integratsiyasi keyingi vazifada amalga oshiriladi.",
        })

    @action(detail=False, methods=["get"], url_path="kpis")  # /credit/kpis/
    def kpis(self, request):
        """Credit KPI raqamlari (stat-card uchun)."""
        return Response(selectors.get_credit_kpis())
