"""
Orders domain — multi-stage lifecycle (TZ §14).
"""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class OrderStatus(models.TextChoices):
    """Order lifecycle stages — TZ §14"""
    INQUIRY = "inquiry", _("So'rov (Inquiry)")
    OFFER = "offer", _("Taklif (Offer)")
    NEGOTIATION = "negotiation", _("Muzokara (Negotiation)")
    ESCROW_PENDING = "escrow_pending", _("To'lov kutilmoqda (Escrow Pending)")
    PAID = "paid", _("To'langan (Paid)")
    STARTED = "started", _("Boshlangan (Started)")
    PRODUCTION = "production", _("Ishlab chiqarilmoqda (Production)")
    SHIPPING = "shipping", _("Yetkazib berilmoqda (Shipping)")
    DELIVERED = "delivered", _("Yetkazib berildi (Delivered)")
    COMPLETED = "completed", _("Yakunlandi (Completed)")
    CANCELED = "canceled", _("Bekor qilindi (Canceled)")
    DISPUTED = "disputed", _("Bahsli (Disputed)")


class Order(BaseModel):
    """
    Core Order row.
    
    Ties a customer to a seller and tracks the lifecycle.
    """
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="customer_orders",
        verbose_name=_("Mijoz"),
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="seller_orders",
        verbose_name=_("Sotuvchi"),
    )
    
    status = models.CharField(
        max_length=24,
        choices=OrderStatus.choices,
        default=OrderStatus.INQUIRY,
        db_index=True,
    )
    
    # Financials
    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name=_("Umumiy narx"),
    )
    escrow_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text="Escrow'da ushlab turilgan summa",
    )
    
    # Shipping Info
    shipping_address = models.TextField(blank=True, verbose_name=_("Yetkazib berish manzili"))
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name=_("Aloqa telefoni"))
    
    # Metadata
    notes = models.TextField(blank=True, verbose_name=_("Izohlar"))
    
    class Meta:
        db_table = "orders_order"
        ordering = ["-created_at"]
        verbose_name = _("Buyurtma")
        verbose_name_plural = _("Buyurtmalar")

    def __str__(self) -> str:
        return f"Order {self.id} ({self.status})"


class OrderItem(BaseModel):
    """
    Individual products within an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    # Variant information (if any)
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    
    class Meta:
        db_table = "orders_item"
        verbose_name = _("Buyurtma elementi")
        verbose_name_plural = _("Buyurtma elementlari")

    def __str__(self) -> str:
        return f"{self.product.title_uz} x {self.quantity}"
