"""
Selectors for apps.management — faqat o'qish (read-only) querylar.

Loyiha standartiga ko'ra (apps app skeleton):
    - selectors.py = optimized querysets, no mutations
    - services.py  = writes/transactions/side-effects

Bu modul Bittada ERP barcha "list/detail" sahifalari uchun ma'lumot manbai.
DRF ViewSet'lar va Django Template Views bir xil selector'larni chaqiradi —
shu orqali biz "ikki ko'rinish, bitta haqiqat" printsipiga rioya qilamiz.
"""
from __future__ import annotations  # Annotatsiya kelajak rejimi

from decimal import Decimal  # Pul hisoblari uchun (float emas)
from typing import Any  # Dict tiplar uchun

from django.db.models import Count, QuerySet, Sum  # Aggregatsiya va tip

from apps.orders.models import Order, OrderStatus  # Buyurtmalar (Sales/Escrow uchun)
from apps.products.models import Product, ProductStatus  # Mahsulotlar


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTS — Mahsulotlar selectorlari
# ─────────────────────────────────────────────────────────────────────────────

def list_products_for_management(user) -> QuerySet[Product]:
    """ERP ro'yxati uchun mahsulotlar (rolga mos filterlash bilan).

    - Superuser/Admin → barcha mahsulotlar
    - Seller → faqat o'zining mahsulotlari (seller=user)

    Args:
        user: request.user (autentifikatsiyalangan ERP foydalanuvchisi)

    Returns:
        Optimallashtirilgan QuerySet (select_related + prefetch_related).
    """
    qs = Product.objects.select_related("category", "seller").prefetch_related("images")  # N+1 oldini olish

    # Yuqori darajadagilar hammasini ko'radi (admin/super_admin/staff/superuser)
    if user.is_superuser or user.is_staff:
        return qs
    if getattr(user, "role", "") in {"admin", "super_admin"}:
        return qs

    # Sotuvchi — faqat o'zining mahsulotlari (yo'q bo'lsa bo'sh QuerySet)
    return qs.filter(seller=user)


def get_product_kpis() -> dict[str, int]:
    """Mahsulotlar bo'limi uchun KPI raqamlari (sahifa yuqorisidagi kartochkalar)."""
    return {  # Bitta query bilan bo'lib, faqat 3 ta count qiymati qaytariladi
        "total": Product.objects.count(),  # Jami mahsulotlar
        "published": Product.objects.filter(status=ProductStatus.PUBLISHED).count(),  # Nashr etilgan
        "draft": Product.objects.exclude(status=ProductStatus.PUBLISHED).count(),  # Qoralama/arxiv
    }


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS — Savdo (Sales) selectorlari
# ─────────────────────────────────────────────────────────────────────────────

def list_orders_for_management(user) -> QuerySet[Order]:
    """ERP Savdo ro'yxati uchun buyurtmalar (rolga mos filterlash).

    - Superuser/Admin → barcha buyurtmalar
    - Seller → faqat o'zining sotuvlari (seller=user)
    """
    qs = Order.objects.select_related("customer", "seller").order_by("-created_at")  # Yangilari yuqorida

    if user.is_superuser or user.is_staff:  # Yuqori daraja → hammasini ko'radi
        return qs
    if getattr(user, "role", "") in {"admin", "super_admin"}:
        return qs
    return qs.filter(seller=user)  # Sotuvchi — faqat o'zining sotuvlari


def get_sales_kpis() -> dict[str, Any]:
    """Savdo (Sales) bo'limi uchun KPI raqamlari.

    Returns:
        {
            "total_orders": int,        # jami buyurtma
            "active_orders": int,       # boshlangan/ishlab chiqarilayotgan/yetkazilayotgan
            "new_inquiries": int,       # yangi so'rovlar
            "completed": int,           # yakunlangan
            "gmv": Decimal,             # Gross Merchandise Value (yakunlanganlar yig'indisi)
        }
    """
    active_statuses = [  # "Faol" deb hisoblanadigan holatlar (TZ §14)
        OrderStatus.STARTED,  # Boshlangan
        OrderStatus.PRODUCTION,  # Ishlab chiqarilmoqda
        OrderStatus.SHIPPING,  # Yetkazib berilmoqda
    ]

    total_count = Order.objects.count()  # Bitta count query
    active_count = Order.objects.filter(status__in=active_statuses).count()  # Faol
    new_count = Order.objects.filter(status=OrderStatus.INQUIRY).count()  # Yangi so'rov
    completed_count = Order.objects.filter(status=OrderStatus.COMPLETED).count()  # Yakunlangan

    gmv_agg = Order.objects.filter(status=OrderStatus.COMPLETED).aggregate(  # Yakunlangan summa
        total=Sum("total_price"),  # SQL SUM(total_price)
    )

    return {
        "total_orders": total_count,
        "active_orders": active_count,
        "new_inquiries": new_count,
        "completed": completed_count,
        "gmv": gmv_agg["total"] or Decimal("0"),  # NULL bo'lsa 0
    }


# ─────────────────────────────────────────────────────────────────────────────
# ESCROW — Escrow Fund selectorlari (Order modeli ustida)
# ─────────────────────────────────────────────────────────────────────────────

def list_escrow_orders(user) -> QuerySet[Order]:
    """Escrow'da pul ushlab turilgan buyurtmalar.

    "Muzlatilgan" deb hisoblanadi: pul to'langan, lekin sotuvchiga to'liq berilmagan
    (status: ESCROW_PENDING, PAID, STARTED, PRODUCTION, SHIPPING, DISPUTED).
    """
    frozen_statuses = [  # Pul ushlab turilgan holatlar
        OrderStatus.ESCROW_PENDING,
        OrderStatus.PAID,
        OrderStatus.STARTED,
        OrderStatus.PRODUCTION,
        OrderStatus.SHIPPING,
        OrderStatus.DISPUTED,
    ]
    qs = Order.objects.filter(  # Asosiy filter: faqat escrow_amount > 0 bo'lganlari
        status__in=frozen_statuses,
        escrow_amount__gt=0,  # 0 dan katta bo'lishi shart (aks holda escrow yo'q)
    ).select_related("customer", "seller").order_by("-created_at")  # Optimizatsiya

    if user.is_superuser or user.is_staff:  # Yuqori daraja → hammasi
        return qs
    if getattr(user, "role", "") in {"admin", "super_admin"}:
        return qs
    return qs.filter(seller=user)  # Sotuvchi — faqat o'zining escrow'lari


def get_escrow_kpis() -> dict[str, Any]:
    """Escrow Fund KPI raqamlari."""
    frozen_statuses = [  # Yuqoridagi list bilan bir xil
        OrderStatus.ESCROW_PENDING,
        OrderStatus.PAID,
        OrderStatus.STARTED,
        OrderStatus.PRODUCTION,
        OrderStatus.SHIPPING,
        OrderStatus.DISPUTED,
    ]
    agg = Order.objects.filter(status__in=frozen_statuses).aggregate(  # Yagona aggregatsiya query
        total=Sum("escrow_amount"),  # Jami muzlatilgan summa
        count=Count("id"),  # Jami buyurtma soni (escrow holatda)
    )
    pending_count = Order.objects.filter(status=OrderStatus.ESCROW_PENDING).count()  # Kutilmoqda
    disputed_count = Order.objects.filter(status=OrderStatus.DISPUTED).count()  # Bahsli

    return {
        "frozen_total": agg["total"] or Decimal("0"),  # NULL → 0
        "frozen_count": agg["count"] or 0,
        "pending_count": pending_count,
        "disputed_count": disputed_count,
    }


# ─────────────────────────────────────────────────────────────────────────────
# USERS — Foydalanuvchilar boshqaruvi selectorlari
# ─────────────────────────────────────────────────────────────────────────────

def list_users_for_management() -> QuerySet:
    """Faqat admin/super_admin uchun: barcha foydalanuvchilarni ro'yxatlash."""
    from apps.users.models import User  # Lazy import (circular avoidance)
    return User.objects.all().order_by("-created_at")  # Yangilari yuqorida


def list_blacklist_users() -> QuerySet:
    """Qora ro'yxat: is_active=False bo'lgan foydalanuvchilar."""
    from apps.users.models import User  # Lazy import
    return User.objects.filter(is_active=False).order_by("-created_at")  # Bloklanganlar


def get_users_kpis() -> dict[str, int]:
    """Foydalanuvchilar bo'limi KPI raqamlari."""
    from apps.users.models import User, Role  # Lazy import (apps yuklanish tartibi)
    return {
        "total": User.objects.count(),  # Jami foydalanuvchilar
        "customers": User.objects.filter(role=Role.CUSTOMER).count(),  # Mijozlar
        "sellers": User.objects.filter(role=Role.SELLER).count(),  # Sotuvchilar
        "blacklisted": User.objects.filter(is_active=False).count(),  # Bloklangan
    }


# ─────────────────────────────────────────────────────────────────────────────
# CREDIT — Bittada Credit Economy (vaqtinchalik placeholder)
# ─────────────────────────────────────────────────────────────────────────────

def get_credit_kpis() -> dict[str, Any]:
    """Credit Economy KPI raqamlari (TZ §15 — kelajakda apps.billing.models bilan to'liq integratsiya).

    Hozircha placeholder: apps.billing modeli to'liq amalga oshmagan bo'lsa,
    dummy qiymatlar qaytariladi. Keyingi vazifada haqiqiy hisoblash bilan almashtiriladi.
    """
    # TODO (keyingi vazifa): apps.billing.models.CreditAccount/CreditTransaction'dan haqiqiy ma'lumot
    return {
        "active_credits": Decimal("450200"),  # Aylanmadagi credit (placeholder)
        "circulation_status": "active",  # Tizim holati (active/paused/halted)
        "active_holders": 0,  # Hisob egalarining soni (kelajakda User.creditaccount_set.count())
    }
