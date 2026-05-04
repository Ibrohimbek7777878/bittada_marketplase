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


class CreditAction(models.TextChoices):
    """TZ §16 - Credits gate paid actions"""
    REVEAL_PHONE = "reveal_phone", "Telefonni ko'rish"
    REVEAL_EMAIL = "reveal_email", "Emailni ko'rish"
    OPEN_CHAT = "open_chat", "Chatni ochish"
    PRIORITY_LEAD = "priority_lead", "Navbatdan tashqari lead"
    BOOST_LISTING = "boost_listing", "E'lonni yuqoriga ko'tarish"


class CreditPrice(BaseModel):
    """
    TZ §16 - Har bir action uchun credit narxi (admin configurable).
    Super Admin paneldan o'zgartiriladi.
    """
    action = models.CharField(
        max_length=20,
        choices=CreditAction.choices,
        unique=True,
        verbose_name="Action"
    )
    credits = models.PositiveIntegerField(
        default=1,
        verbose_name="Credit soni"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )

    class Meta:
        verbose_name = "Credit narxi"
        verbose_name_plural = "Credit narxlari"

    def __str__(self) -> str:
        return f"{self.get_action_display()} - {self.credits} credit"


class CreditTransaction(BaseModel):
    """
    TZ §16 - Credit ishlatish tarixi.
    Kim, qachon, qaysi action uchun credit ishlatgan.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="credit_transactions",
        verbose_name="Foydalanuvchi"
    )
    action = models.CharField(
        max_length=20,
        choices=CreditAction.choices,
        verbose_name="Action"
    )
    credits_used = models.PositiveIntegerField(
        verbose_name="Ishlatilgan credit"
    )
    # Qaysi sotuvchi profili uchun ishlatilgan
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_credit_spends",
        verbose_name="Maqsad foydalanuvchi"
    )
    # Lead conversion tracking
    converted_to_order = models.BooleanField(
        default=False,
        verbose_name="Buyurtmaga aylanganmi?"
    )
    # Seller ko'radi: kim contact'ini ochgan
    viewed_by_seller_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Sotuvchi ko'rgan vaqti"
    )

    class Meta:
        verbose_name = "Credit tranzaksiyasi"
        verbose_name_plural = "Credit tranzaksiyalari"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} → {self.action} ({self.credits_used} credit)"
