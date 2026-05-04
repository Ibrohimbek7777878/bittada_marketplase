"""
Models for the billing domain.
Handles user wallets, balance tracking, and transaction history.
"""
from __future__ import annotations

from django.db import models
from django.conf import settings
from core.models import BaseModel

class Wallet(BaseModel):
    """
    Foydalanuvchi hamyoni.
    Har bir foydalanuvchi uchun bitta hamyon mavjud bo'ladi.
    """
    # Foydalanuvchi bilan 1:1 bog'liqlik (har bir userda bitta hamyon)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
        verbose_name="Foydalanuvchi"
    )
    # Hozirgi balans (Decimal — aniqlik uchun, 20 ta raqam, 2 tasi verguldan keyin)
    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        verbose_name="Balans"
    )
    # Muzlatilgan mablag'lar (Escrow yoki buyurtmalar uchun)
    frozen_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        verbose_name="Muzlatilgan balans"
    )
    # Hamyon holati
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktivmi?"
    )

    class Meta:
        verbose_name = "Hamyon"
        verbose_name_plural = "Hamyonlar"

    def __str__(self) -> str:
        # Hamyonni identifikatsiyalash uchun user emailini qaytaramiz
        return f"{self.user.email} hamyoni ({self.balance})"


class TransactionType(models.TextChoices):
    """Tranzaksiya turlari: To'ldirish, Yechish, O'tkazma, Muzlatish, Qulfdan chiqarish."""
    DEPOSIT = "deposit", "To'ldirish"
    WITHDRAW = "withdraw", "Yechish"
    TRANSFER = "transfer", "O'tkazma"
    FREEZE = "freeze", "Muzlatish"
    UNFREEZE = "unfreeze", "Muzlatishdan chiqarish"
    PAYMENT = "payment", "To'lov"


class TransactionStatus(models.TextChoices):
    """Tranzaksiya holatlari."""
    PENDING = "pending", "Kutilmoqda"
    COMPLETED = "completed", "Bajarildi"
    FAILED = "failed", "Xatolik"
    CANCELLED = "cancelled", "Bekor qilindi"


class Transaction(BaseModel):
    """
    Moliyaviy tranzaksiyalar tarixi.
    Barcha pul harakatlari shu yerda qayd etiladi.
    """
    # Qaysi hamyonga tegishli
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Hamyon"
    )
    # Tranzaksiya turi (deposit, withdraw, etc.)
    kind = models.CharField(
        max_length=20, # CharField uchun max_length ishlatiladi
        choices=TransactionType.choices,
        verbose_name="Turi"
    )
    # Tranzaksiya holati
    status = models.CharField(
        max_length=20, # CharField uchun max_length ishlatiladi
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
        verbose_name="Holati"
    )
    # Summa (ijobiy qiymat)
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Summa"
    )
    # Izoh (foydalanuvchi yoki tizim uchun)
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Izoh"
    )
    # Tashqi tizim IDsi (masalan: Payme, Click yoki Stripe tranzaksiya IDsi)
    external_id = models.CharField(
        max_length=255, # CharField uchun max_length ishlatiladi
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Tashqi ID"
    )
    # Qo'shimcha meta ma'lumotlar (JSON formatida)
    meta_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Meta ma'lumotlar"
    )

    class Meta:
        verbose_name = "Tranzaksiya"
        verbose_name_plural = "Tranzaksiyalar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        # Tranzaksiyani qisqacha tavsiflash
        return f"{self.kind} - {self.amount} ({self.status})"
