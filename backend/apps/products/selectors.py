"""
Read queries for `products`.

Pure functions returning querysets / dicts. No side effects, no writes.
Optimize with `select_related` / `prefetch_related` here, not in views.

Daxlsizlik eslatma: bu fayl avval faqat docstring va `from __future__`
qatoridan iborat edi. Mavjud hech qanday funksiyaga aralashmasdan,
yangi `get_products_by_seller` selektorini qo'shamiz — uni
`apps/users/views.py`'dagi `SellerPublicProfileView` chaqiradi.
"""
from __future__ import annotations  # Kelajakdagi type hint sintaksisi (str literal sifatida)

# Type hinting uchun QuerySet importi (Django 5+ generic mavjud)
from django.db.models import QuerySet

# Mahsulot modeli va status enumeratsiyasi (faqat nashr etilganlarni qaytarish uchun)
from .models import Product, ProductStatus


def get_products_by_seller(
    seller_id,  # Sotuvchi User obyektining UUID identifikatori (str/UUID)
    *,  # Quyidagi argumentlar — faqat nomlangan (positional bo'lmasin)
    only_published: bool = True,  # Default: faqat published mahsulotlar (public profil uchun)
    limit: int | None = None,  # Default: limit yo'q (qaytarilgan QuerySet keyin slice qilinishi mumkin)
) -> QuerySet[Product]:  # Return type: Product QuerySet (lazy — view ichida iterate qilinadi)
    """
    Berilgan sotuvchi (User UUID) bo'yicha mahsulotlar QuerySet'ini qaytaradi.

    Public profile sahifasi uchun mo'ljallangan: N+1 muammosini oldini olish
    uchun `select_related("category")` va `prefetch_related("images")` qo'shilgan
    (mahsulot kartochkasi rasm va kategoriya nomini ko'rsatadi).

    Argumentlar:
        seller_id: User UUID — `request.user.id` yoki URL'dan olingan seller.id
        only_published: True bo'lsa faqat ProductStatus.PUBLISHED qaytariladi
                       (public profil uchun har doim True bo'lishi kerak,
                        sotuvchi o'zining draft'larini ham ko'rsa False bilan chaqiriladi).
        limit: int berilsa — QuerySet'ga `[:limit]` qo'llaniladi (None bo'lsa cheksiz).

    Qaytaradi:
        QuerySet[Product] — yangi mahsulotlar yuqorida (`-created_at`).
    """
    # Asosiy queryset — seller bo'yicha filter va N+1 oldini olish (related lookup)
    qs = (
        Product.objects  # Default soft-delete manager (deleted_at IS NULL)
        .filter(seller_id=seller_id)  # Faqat shu sotuvchining mahsulotlari
        .select_related("category")  # category JOIN bilan keladi (kartochkada nom kerak)
        .prefetch_related("images")  # 1+1 query: barcha rasmlar bitta qo'shimcha so'rovda olinadi
        .order_by("-created_at")  # Yangiroq mahsulotlar yuqorida
    )

    # Public profil ko'rsatadigan bo'lsa — faqat tasdiqlangan/nashr etilgan
    if only_published:  # Default — True
        qs = qs.filter(status=ProductStatus.PUBLISHED)  # Faqat "published" status

    # Agar chaqiruvchi cheklov bersa — slice qo'llaymiz
    if limit is not None:  # None bo'lmasa
        qs = qs[:limit]  # QuerySet slicing (DB darajasida LIMIT)

    return qs  # Lazy QuerySet — view ichida iterate qilinadi
