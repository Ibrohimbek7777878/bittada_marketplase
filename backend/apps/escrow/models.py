"""
Models for the escrow domain.
Manages secure payments where funds are held by the platform until conditions are met.
"""
from __future__ import annotations

from django.db import models
from core.models import BaseModel

class EscrowStatus(models.TextChoices):
    """Escrow holatlari."""
    HELD = "held", "Mablag' ushlab turilibdi (Muzlatilgan)"
    RELEASED = "released", "Mablag' sotuvchiga o'tkazildi"
    REFUNDED = "refunded", "Mablag' xaridorga qaytarildi"
    DISPUTED = "disputed", "Bahsli holat"


class Escrow(BaseModel):
    """
    Escrow obyekti.
    Har bir xavfsiz bitim uchun yaratiladi.
    """
    # Buyurtma bilan bog'liqlik (har bir buyurtma uchun bitta escrow)
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="escrow",
        verbose_name="Buyurtma"
    )
    # Sotuvchi (mablag'ni qabul qiluvchi)
    seller = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="seller_escrows",
        verbose_name="Sotuvchi"
    )
    # Xaridor (mablag'ni to'lovchi)
    buyer = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="buyer_escrows",
        verbose_name="Xaridor"
    )
    # Bitim summasi
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Summa"
    )
    # Escrow holati (CharField da max_digits bo'lmaydi, max_length ishlatiladi)
    status = models.CharField(
        max_length=20, # Belgilar soni cheklovi (TZ 15)
        choices=EscrowStatus.choices, # Tanlov variantlari
        default=EscrowStatus.HELD, # Standart holat
        verbose_name="Holati"
    )
    # Bahsli holat bo'yicha izoh (agar bo'lsa)
    dispute_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name="Bahs sababi"
    )

    class Meta:
        verbose_name = "Escrow bitimi"
        verbose_name_plural = "Escrow bitimlari"

    def __str__(self) -> str:
        # Escrow bitimini identifikatsiyalash
        return f"Escrow #{self.id[:8]} - {self.amount} ({self.status})"
