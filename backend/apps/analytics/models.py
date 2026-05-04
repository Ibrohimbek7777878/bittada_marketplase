"""
TZ §18 - Analytics domain.
Seller dashboard + Admin dashboard tracking.
"""
from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class ProductView(BaseModel):
    """
    TZ §18 - Mahsulot ko'rishlari (unique + total).
    Denormalized cache for fast seller dashboard.
    """
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="view_records",
        verbose_name=_("Mahsulot")
    )
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="viewed_products",
        verbose_name=_("Ko'ruvchi")
    )
    # For anonymous users
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP manzil")
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_("User-Agent")
    )
    source = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Manba"),
        help_text=_("organic, search, ads, referral, direct")
    )

    class Meta:
        verbose_name = "Mahsulot ko'rishi"
        verbose_name_plural = "Mahsulot ko'rishlari"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["viewer", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.product} viewed by {self.viewer or self.ip_address}"


class ProfileView(BaseModel):
    """
    TZ §18 - Profil ko'rishlari (seller uchun).
    Kim sotuvchi profilini ko'rgan.
    """
    profile = models.ForeignKey(
        "users.Profile",
        on_delete=models.CASCADE,
        related_name="view_records",
        verbose_name=_("Profil")
    )
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="viewed_profiles",
        verbose_name=_("Ko'ruvchi")
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP manzil")
    )
    # Seller analytics: who viewed contact
    contact_unlocked = models.BooleanField(
        default=False,
        verbose_name=_("Contact ochilganmi?")
    )

    class Meta:
        verbose_name = "Profil ko'rishi"
        verbose_name_plural = "Profil ko'rishlari"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.profile} viewed by {self.viewer or self.ip_address}"


class DailyStats(BaseModel):
    """
    TZ §18 - Seller uchun kunlik statistika (denormalized).
    Fast dashboard charts without heavy aggregation queries.
    """
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_stats",
        limit_choices_to={"role__in": ["seller", "internal_supplier"]},
        verbose_name=_("Sotuvchi")
    )
    date = models.DateField(
        verbose_name=_("Sana")
    )
    # Product metrics
    product_views = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Mahsulot ko'rishlari")
    )
    product_views_unique = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Unikal ko'rishlar")
    )
    add_to_cart_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Savatchaga qo'shilgan")
    )
    wishlist_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sevimlilarga qo'shilgan")
    )
    contact_clicks = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Contact bosishlar")
    )
    # Order metrics
    inquiries = models.PositiveIntegerField(
        default=0,
        verbose_name=_("So'rovlar")
    )
    orders = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Buyurtmalar")
    )
    revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name=_("Daromad")
    )
    # Source breakdown
    organic_views = models.PositiveIntegerField(default=0)
    search_views = models.PositiveIntegerField(default=0)
    ads_views = models.PositiveIntegerField(default=0)
    referral_views = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Kunlik statistika"
        verbose_name_plural = "Kunlik statistikalar"
        unique_together = ["seller", "date"]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.seller} @ {self.date}: {self.product_views} views"


class ConversionEvent(BaseModel):
    """
    TZ §18 - Conversion funnel tracking.
    view → cart → contact → inquiry → order
    """
    class EventType(models.TextChoices):
        VIEW = "view", "Ko'rish"
        CART = "cart", "Savatchaga qo'shish"
        CONTACT = "contact", "Contact ochish"
        INQUIRY = "inquiry", "So'rov yuborish"
        OFFER = "offer", "Taklif"
        ORDER = "order", "Buyurtma"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversion_events",
        verbose_name=_("Foydalanuvchi")
    )
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        verbose_name=_("Event turi")
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversion_events",
        verbose_name=_("Mahsulot")
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_conversion_events",
        limit_choices_to={"role__in": ["seller", "internal_supplier"]},
        verbose_name=_("Sotuvchi")
    )
    value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Qiymat")
    )

    class Meta:
        verbose_name = "Conversion hodisasi"
        verbose_name_plural = "Conversion hodisalari"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event_type} @ {self.seller} by {self.user}"
