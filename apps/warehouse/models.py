"""
TZ §17 - Warehouse & Stock domain.
Multi-warehouse per seller with stock statuses and ERP sync.
"""
from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class WarehouseType(models.TextChoices):
    """TZ §17 - Ombor turlari"""
    HOME = "home", "O'z uy/ofis"
    EXTERNAL = "external", "Ijaraga olingan ombor"
    SUPPLIER = "supplier", "Yetkazib beruvchi (drop-ship)"


class Warehouse(BaseModel):
    """
    TZ §17 - Sotuvchining ombori.
    Har bir sotuvchida bir nechta ombor bo'lishi mumkin.
    """
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="warehouses",
        limit_choices_to={"role__in": ["seller", "internal_supplier"]},
        verbose_name=_("Sotuvchi")
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Ombor nomi")
    )
    warehouse_type = models.CharField(
        max_length=20,
        choices=WarehouseType.choices,
        default=WarehouseType.HOME,
        verbose_name=_("Ombor turi")
    )
    address = models.TextField(
        verbose_name=_("Manzil"),
        help_text=_("To'liq manzil")
    )
    # Geo coordinates for distance-aware delivery
    geo_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("Kenglik")
    )
    geo_lng = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("Uzunlik")
    )
    # ERP integration
    external_erp_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Tashqi ERP ID")
    )
    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Oxirgi sinxronlash vaqti")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol")
    )

    class Meta:
        verbose_name = "Ombor"
        verbose_name_plural = "Omborlar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_warehouse_type_display()})"


class StockStatus(models.TextChoices):
    """TZ §17 - Zaxira holatlari"""
    AVAILABLE = "available", "Mavjud"
    RESERVED = "reserved", "Zaxiraga olingan"
    OUT_OF_STOCK = "out_of_stock", "Tugagan"
    INCOMING = "incoming", "Yo'lda/kutilmoqda"


class Stock(BaseModel):
    """
    TZ §17 - SKU/Variant bo'yicha zaxira har bir omborda.
    """
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="stocks",
        verbose_name=_("Ombor")
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="warehouse_stocks",
        verbose_name=_("Mahsulot")
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="warehouse_stocks",
        verbose_name=_("Variant")
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Miqdori")
    )
    status = models.CharField(
        max_length=20,
        choices=StockStatus.choices,
        default=StockStatus.AVAILABLE,
        verbose_name=_("Holat")
    )
    # Buyurtma uchun zaxiraga olingan
    reserved_qty = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Zaxiraga olingan")
    )
    # Qo'shimcha ma'lumotlar
    note = models.TextField(
        blank=True,
        verbose_name=_("Izoh")
    )

    class Meta:
        verbose_name = "Zaxira"
        verbose_name_plural = "Zaxiralar"
        unique_together = ["warehouse", "product", "variant"]
        indexes = [
            models.Index(fields=["product", "status"]),
            models.Index(fields=["warehouse", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.product} @ {self.warehouse}: {self.quantity}"


class Reservation(BaseModel):
    """
    TZ §17 - Buyurtma uchun zaxiraga olingan tovarlar.
    Buyurtma bekor bo'lsa, zaxira qaytariladi.
    """
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name=_("Buyurtma")
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name=_("Zaxira")
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("Miqdori")
    )
    is_released = models.BooleanField(
        default=False,
        verbose_name=_("Qaytarilganmi?")
    )
    released_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Qaytarilgan vaqti")
    )

    class Meta:
        verbose_name = "Zaxira olish"
        verbose_name_plural = "Zaxira olishlar"

    def __str__(self) -> str:
        return f"Order {self.order_id}: {self.quantity} x {self.stock.product}"
