"""
Read queries for `showroom`.

Pure functions returning querysets / dicts. No side effects, no writes.
Optimize with `select_related` / `prefetch_related` here, not in views.

Daxlsizlik eslatma: bu fayl avval faqat docstring va `from __future__`
qatoridan iborat edi. Hech qanday mavjud funksiyaga aralashmasdan,
yangi `get_portfolio_by_seller` selektorini qo'shamiz —
`apps/users/views.py`'dagi `SellerPublicProfileView` ishlatadi.
"""
from __future__ import annotations  # Kelajakdagi type hint sintaksisi (str literal sifatida)

# Type hinting uchun QuerySet importi
from django.db.models import QuerySet

# Yangi yaratilgan PortfolioItem modeli (apps/showroom/models.py)
from .models import PortfolioItem


def get_portfolio_by_seller(
    seller_id,  # Sotuvchi User obyektining UUID identifikatori (str/UUID)
    *,  # Quyidagi argumentlar — faqat nomlangan
    only_published: bool = True,  # Default: faqat is_published=True elementlar (public profil uchun)
    limit: int | None = None,  # Default: limit yo'q
) -> QuerySet[PortfolioItem]:  # Return type: PortfolioItem QuerySet (lazy)
    """
    Berilgan sotuvchi (User UUID) bo'yicha portfolio elementlari QuerySet'i.

    Public profile sahifasida "Portfolio" tabni to'ldirish uchun ishlatiladi.
    Karta tasvirlanishi uchun maydonlar to'g'ridan-to'g'ri model ustida bor —
    select_related kerak emas (FK rasm ichida emas, ImageField).

    Argumentlar:
        seller_id: User UUID — sotuvchining identifikatori
        only_published: True bo'lsa faqat is_published=True qaytariladi
                       (public profile har doim True chaqiradi).
        limit: int berilsa — QuerySet'ga `[:limit]` qo'llaniladi.

    Qaytaradi:
        QuerySet[PortfolioItem] — order ASC, keyin -created_at (yangi yuqorida).
    """
    # Asosiy queryset — seller bo'yicha filter
    qs = (
        PortfolioItem.objects  # Default manager
        .filter(seller_id=seller_id)  # Faqat shu sotuvchining portfoliosi
        # ordering Meta'da belgilangan (order ASC, -created_at) — qo'shimcha order_by shart emas
    )

    # Public profil ko'rsatadigan bo'lsa — faqat ko'rinishga ruxsat berilganlari
    if only_published:  # Default — True
        qs = qs.filter(is_published=True)  # is_published=True bo'lganlari

    # Agar chaqiruvchi cheklov bersa — slice qo'llaymiz
    if limit is not None:  # None bo'lmasa
        qs = qs[:limit]  # DB darajasida LIMIT

    return qs  # Lazy QuerySet
