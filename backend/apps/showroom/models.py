"""
Models for `showroom`.

Hozircha bir model bor: PortfolioItem — sotuvchi (usta/dizayner/ishlab chiqaruvchi)
o'zining bajargan ishlarini (foto + tavsif) sahifasiga qo'yishi uchun.

Bu model `apps/users/views.py`'dagi `SellerPublicProfileView` uchun kerak —
agar sotuvchi kamida bitta PortfolioItem qo'shgan bo'lsa, profilida "Portfolio"
tab ko'rinadi (mahsulotdan alohida, instagram-uslubdagi feed sifatida).

Model `core.models.BaseModel`'dan meros oladi:
- id (UUID, primary key)
- created_at (DateTimeField, auto_now_add)
- updated_at (DateTimeField, auto_now)
- ordering = ["-created_at"] (yangi ish — yuqorida)
"""
from __future__ import annotations  # Kelajakdagi type hint sintaksisi (Python 3.7+)

# Django ORM moduli — model maydonlari va Meta klassi uchun
from django.db import models
# Loyiha settings — AUTH_USER_MODEL referensi orqali User modeliga bog'lanish uchun
from django.conf import settings
# i18n yordamchisi — keyinchalik tarjima qilish mumkin bo'lgan matnlar uchun
from django.utils.translation import gettext_lazy as _

# Loyihaning umumiy abstrakt modeli (UUID id + created_at/updated_at + default ordering)
from core.models import BaseModel


class PortfolioItem(BaseModel):  # Sotuvchi portfoliosidagi yakka karta (1 ta tugatilgan ish)
    """
    Sotuvchining portfolio elementi (Instagram-style feed kartasi).

    Mantiq: usta/dizayner o'zining oldingi ishlarini sotuvchi profili
    tab'ida ko'rsatishi uchun yaratiladi. Bu mahsulot emas (sotuvga emas),
    balki "men nima qila olaman" namunasi.

    Daxlsizlik: bu yangi model bo'lib, mavjud showroom kodi bilan
    konflikt yo'q (showroom/models.py awal bo'sh edi).
    """

    # === Egasi (seller) ===
    # FK foydalanuvchiga: portfolio ushbu seller'ga tegishli
    # related_name="portfolio_items" — `user.portfolio_items.all()` orqali kirishimiz mumkin
    # on_delete=CASCADE — seller o'chirilsa, uning portfoliosi ham o'chiriladi (audit log uchun showroom alohida tekshiriladi)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # User modeliga bog'liq, settings orqali (circular import oldini olish)
        on_delete=models.CASCADE,  # Seller o'chsa - uning portfoliosi ham o'chadi
        related_name="portfolio_items",  # user.portfolio_items.all() ko'rinishida ishlatiladi
        verbose_name=_("Sotuvchi"),  # Admin panelda ko'rsatiladigan nom
        # Faqat sotuvchi/ichki ta'minotchi rolidagi userlar portfolio yaratishi mumkin
        limit_choices_to={"role__in": ["seller", "internal_supplier"]},
    )

    # === Asosiy mazmun maydonlari ===
    # Sarlavha — kartada katta shrift bilan ko'rsatiladi (maks 200 belgi)
    title = models.CharField(
        max_length=200,  # Sarlavha 200 belgidan oshmasin
        verbose_name=_("Sarlavha"),  # Admin uchun nom
    )
    # Tavsif — ko'p qatorli matn (ish haqida batafsil ma'lumot, ixtiyoriy)
    description = models.TextField(
        blank=True,  # Bo'sh bo'lishi mumkin
        verbose_name=_("Tavsif"),  # Admin uchun nom
    )
    # Asosiy rasm — portfolioning visual qismi (majburiy, chunki feed tasvirsiz ishlamaydi)
    cover_image = models.ImageField(
        upload_to="showroom/portfolio/%Y/%m/",  # Yuklash yo'li (yil/oy bo'yicha qatlamli)
        verbose_name=_("Asosiy rasm"),  # Admin uchun nom
    )

    # === Qo'shimcha metadata ===
    # Geografik joy (qaysi shahar/kvartal) — qo'shimcha context, ixtiyoriy
    location = models.CharField(
        max_length=200,  # Qisqa joy nomi
        blank=True,  # Bo'sh bo'lishi mumkin
        verbose_name=_("Joylashuv"),  # Admin uchun nom
    )
    # Ish tugatilgan yil — sortlash uchun ham foydali
    completed_year = models.PositiveSmallIntegerField(
        null=True,  # NULL ruxsat etiladi (nomalum bo'lsa)
        blank=True,  # Formada bo'sh qoldirish mumkin
        verbose_name=_("Bajarilgan yil"),  # Admin uchun nom
    )

    # === Ko'rinish va tartib ===
    # Karta ko'rinishini boshqarish — sotuvchi vaqtincha berkitishi mumkin
    is_published = models.BooleanField(
        default=True,  # Default holatda ko'rinadi (yaratilishi bilan)
        db_index=True,  # Tez filter uchun indeks (faqat published'larni tanlashda)
        verbose_name=_("Nashr etilgan"),  # Admin uchun nom
    )
    # Qo'lda tartiblash uchun (kichikroq raqam — yuqori ko'rinadi)
    order = models.PositiveSmallIntegerField(
        default=0,  # Default 0 (yangi qo'shilganda boshqalar bilan teng vaqtga ko'ra saralanadi)
        verbose_name=_("Tartib"),  # Admin uchun nom
    )

    class Meta:  # Modelning baza-darajasidagi sozlamalari
        db_table = "showroom_portfolio_item"  # Aniq jadval nomi (default'dan farqli, app prefix bilan)
        ordering = ["order", "-created_at"]  # Ko'rsatish tartibi: order'ga ko'ra, keyin yangiroq birinchi
        verbose_name = _("Portfolio elementi")  # Admin uchun yakka nom
        verbose_name_plural = _("Portfolio elementlari")  # Admin uchun ko'plik nom
        indexes = [
            # Tez kirish uchun: seller bo'yicha published-larni saralash (ko'p so'raladigan filter)
            models.Index(fields=["seller", "is_published"]),
        ]

    def __str__(self) -> str:  # Admin/log'larda obyektning matn ko'rinishi
        # Ko'rsatish: "Sarlavha (sotuvchi-username)"
        return f"{self.title} ({self.seller.username})"
