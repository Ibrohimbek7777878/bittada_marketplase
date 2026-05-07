"""
Django admin registrations for `showroom`.

Hozircha bitta model: PortfolioItem — sotuvchining bajargan ishlari
katalogi. Admin panelida sotuvchi/ish nomi/yili bo'yicha tezkor
filterlash va qidirish uchun ro'yxatga olamiz.

Daxlsizlik: bu fayl avval bo'sh edi (faqat noqa import). Mavjud
hech qaysi modelga aralashmasdan, faqat yangi PortfolioItem'ni
qo'shamiz.
"""
from __future__ import annotations  # Kelajakdagi type hint sintaksisi

from django.contrib import admin  # Django'ning admin moduli — register dekoratori uchun

from .models import PortfolioItem  # Yuqorida e'lon qilingan yangi model


@admin.register(PortfolioItem)  # Modelni admin saytga ro'yxatga olish
class PortfolioItemAdmin(admin.ModelAdmin):  # PortfolioItem'ning admin sozlamalari
    """Portfolio elementlari uchun admin paneli — qidiruv, filter, list ko'rinishi."""

    # Ro'yxat sahifasida ko'rsatiladigan ustunlar (eng muhim ma'lumotlar)
    list_display = (
        "title",  # Sarlavha (asosiy identifikator)
        "seller",  # Qaysi sotuvchiniki (FK)
        "completed_year",  # Bajarilgan yili
        "is_published",  # Ko'rinishi yoqilganmi
        "order",  # Tartib raqami (qo'lda saralash uchun)
        "created_at",  # Yaratilgan vaqti
    )
    # O'ng tomondagi filter paneli (tez ajratish uchun)
    list_filter = (
        "is_published",  # Faqat nashr etilganlarni ko'rish/yashirish
        "completed_year",  # Yil bo'yicha filter
    )
    # Qidiruv qutisi orqali izlanadigan maydonlar
    search_fields = (
        "title",  # Sarlavha matni
        "description",  # Tavsif ichida
        "seller__username",  # FK: sotuvchining username'i
        "location",  # Joylashuv nomi
    )
    # Ro'yxat sahifasida tahrirlash mumkin bo'lgan ustunlar (tez o'zgartirish uchun)
    list_editable = (
        "is_published",  # Bir bosishda ko'rinishni yoqish/o'chirish
        "order",  # Tartibni o'zgartirish
    )
    # FK uchun avtomatik to'ldirish (large user table ko'rsatilmasligi uchun)
    autocomplete_fields = ("seller",)
    # Default saralash (yangiroqlari yuqorida)
    ordering = ("-created_at",)
    # readonly fields — ID va vaqtlar foydalanuvchi tomonidan tahrirlanmasin
    readonly_fields = ("id", "created_at", "updated_at")
