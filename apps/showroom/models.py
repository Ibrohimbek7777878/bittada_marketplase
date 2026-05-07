"""Models for `showroom`. Add domain rows here."""
from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class PortfolioItem(BaseModel):
    """
    Sotuvchining portfolio elementi (Instagram-style feed kartasi).

    Mantiq: usta/dizayner o'zining oldingi ishlarini sotuvchi profili
    tab'ida ko'rsatishi uchun yaratiladi. Bu mahsulot emas (sotuvga emas),
    balki "men nima qila olaman" namunasi.
    """

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolio_items",
        verbose_name=_("Sotuvchi"),
        limit_choices_to={"role__in": ["seller", "internal_supplier"]},
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Sarlavha"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Tavsif"),
    )
    cover_image = models.ImageField(
        upload_to="showroom/portfolio/%Y/%m/",
        verbose_name=_("Asosiy rasm"),
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Joylashuv"),
    )
    completed_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Bajarilgan yil"),
    )
    is_published = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Nashr etilgan"),
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Tartib"),
    )

    class Meta:
        db_table = "showroom_portfolio_item"
        ordering = ["order", "-created_at"]
        verbose_name = _("Portfolio elementi")
        verbose_name_plural = _("Portfolio elementlari")
        indexes = [
            models.Index(fields=["seller", "is_published"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.seller.username})"
