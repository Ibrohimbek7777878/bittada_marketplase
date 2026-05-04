"""
Services for apps.management — yozish operatsiyalari (transactional).

Loyiha standarti:
    - selectors.py = read-only
    - services.py  = writes (create/update/delete + transactions)

Bu modul biznes mantiqning yozish qismini saqlaydi. ViewSet'lar va views.py shu yerdagi
funksiyalarni chaqiradi (to'g'ridan-to'g'ri Model.objects.create() emas).
"""
from __future__ import annotations  # Annotatsiya kelajak rejimi

from decimal import Decimal  # Pul hisoblari uchun
from typing import Any  # Generic dict tip

from django.db import transaction  # Transactional kontekst (ACID)

from apps.products.models import Product  # Mahsulot modeli


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTS — Yozish operatsiyalari
# ─────────────────────────────────────────────────────────────────────────────

@transaction.atomic  # Funksiya muvaffaqiyatsiz bo'lsa, hech narsa saqlanmaydi (rollback)
def create_product_for_seller(*, seller, payload: dict[str, Any]) -> Product:
    """Sotuvchi uchun yangi mahsulot yaratish.

    Args:
        seller: Mahsulot egasi bo'ladigan User (request.user)
        payload: Validatsiyadan o'tgan ma'lumotlar (title_uz, sku, price, ...)

    Returns:
        Yangi yaratilgan Product obyekti.

    Raises:
        IntegrityError: agar SKU unique cheklash buzilsa (oldindan validate qiling).
    """
    return Product.objects.create(  # Standart Django ORM — mavjud signature (daxlsizlik)
        seller=seller,  # FK biriktirish
        title_uz=payload["title_uz"],  # Nom
        sku=payload["sku"],  # Unique kod
        price=Decimal(str(payload["price"])),  # Decimal'ga aniq aylantirish (str orqali)
        category_id=int(payload["category"]),  # FK ID
        status=payload.get("status", "draft"),  # Default qoralama
        product_type=payload.get("product_type", "standard"),  # Default standart
        description_uz=payload.get("description_uz", ""),  # Bo'sh string ham OK
        stock_qty=int(payload.get("stock_qty") or 0),  # None bo'lsa 0
    )


@transaction.atomic
def update_product(*, product: Product, payload: dict[str, Any]) -> Product:
    """Mavjud mahsulotni yangilash.

    Args:
        product: yangilanadigan Product obyekti
        payload: yangi maydon qiymatlari

    Returns:
        Yangilangan Product obyekti.
    """
    # Faqat ruxsat etilgan maydonlarni yangilaymiz (xavfsizlik — mass-assign oldini olish)
    allowed_fields = {  # Whitelisted maydonlar to'plami
        "title_uz", "title_ru", "title_en",
        "description_uz", "description_ru", "description_en",
        "price", "old_price",
        "stock_qty", "is_in_stock",
        "status", "product_type",
        "primary_material", "style", "condition",
    }
    for field, value in payload.items():  # Payload'dagi har bir maydonni ko'rib chiqish
        if field in allowed_fields:  # Faqat ruxsat etilganlari
            setattr(product, field, value)  # Maydonni yangilash
    product.save()  # Bazaga yozish (signal'lar ishlatiladi)
    return product


@transaction.atomic
def delete_product(*, product: Product) -> None:
    """Mahsulotni o'chirish.

    Eslatma: TZ kelajakda soft-delete (is_active=False) ni xohlashi mumkin.
    Hozircha hard-delete — chunki Product modelida is_active mavjud emas.
    """
    product.delete()  # ORM bilan bazadan o'chirish


# ─────────────────────────────────────────────────────────────────────────────
# USERS — Boshqaruv (admin tomonidan)
# ─────────────────────────────────────────────────────────────────────────────

@transaction.atomic
def block_user(*, user) -> None:
    """Foydalanuvchini qora ro'yxatga olish (is_active=False).

    Bu yerda biz Django'ning standart `is_active` bayrog'idan foydalanamiz.
    Foydalanuvchi bloklangach, login qila olmaydi (axes ham tekshiradi).
    """
    user.is_active = False  # Login imkoniyatini o'chirish
    user.save(update_fields=["is_active"])  # Faqat shu maydonni saqlash (efficient)


@transaction.atomic
def unblock_user(*, user) -> None:
    """Qora ro'yxatdan chiqarish (is_active=True qaytarish)."""
    user.is_active = True
    user.save(update_fields=["is_active"])
