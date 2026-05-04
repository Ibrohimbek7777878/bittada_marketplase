"""
TZ §19 - Blacklist (Private B2B Trust Module).
Fraud/scam tracking visible only to sellers and admins.
"""
from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class BlacklistEntryType(models.TextChoices):
    """TZ §19 - Qora ro'yxatga olish turlari"""
    FRAUD_BUYER = "fraud_buyer", "Firibgar xaridor"
    UNPAID_BUYER = "unpaid_buyer", "To'lamagan xaridor"
    SCAM_SUPPLIER = "scam_supplier", "Firibgar yetkazib beruvchi"
    ABUSE = "abuse", "Haqorat/qo'pol muomala"
    HARASSMENT = "harassment", "Taqib/Terror"
    FAKE_PRODUCT = "fake_product", "Soxta mahsulot"


class BlacklistEntryStatus(models.TextChoices):
    """TZ §19 - Status"""
    PENDING = "pending", "Kutilmoqda"
    VERIFIED = "verified", "Tasdiqlangan"
    DISPUTED = "disputed", "Bahslanmoqda"
    CLEARED = "cleared", "Tozalangan"


class BlacklistEntry(BaseModel):
    """
    TZ §19 - Qora ro'yxatga olish.
    Sellerlar/admins foydalanuvchilarni ro'yxatga olishi mumkin.
    """
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blacklist_reports",
        verbose_name=_("Hisobotchi")
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blacklist_entries",
        verbose_name=_("Maqsad foydalanuvchi")
    )
    # If user not registered, by phone/email
    target_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Maqsad telefoni")
    )
    target_email = models.EmailField(
        blank=True,
        verbose_name=_("Maqsad email")
    )

    entry_type = models.CharField(
        max_length=20,
        choices=BlacklistEntryType.choices,
        verbose_name=_("Tur")
    )
    status = models.CharField(
        max_length=20,
        choices=BlacklistEntryStatus.choices,
        default=BlacklistEntryStatus.PENDING,
        verbose_name=_("Holat")
    )
    reason = models.TextField(
        verbose_name=_("Sabab")
    )
    evidence_files = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Dalil fayllar"),
        help_text=_("Screenshot, chat export, invoice, etc.")
    )

    # Admin moderation
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blacklist_reviews",
        limit_choices_to={"role__in": ["admin", "super_admin"]},
        verbose_name=_("Ko'rib chiqqan")
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Ko'rib chiqilgan vaqti")
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name=_("Admin izohi")
    )

    # Seller voting (credibility)
    upvotes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ovozlar (ha)")
    )
    downvotes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ovozlar (yo'q)")
    )

    class Meta:
        verbose_name = "Qora ro'yxat yozuvi"
        verbose_name_plural = "Qora ro'yxat yozuvlari"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["target_user", "status"]),
            models.Index(fields=["entry_type", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.target_user} - {self.get_entry_type_display()} ({self.status})"


class BlacklistVote(BaseModel):
    """
    TZ §19 - Seller ovozi (credibility uchun).
    """
    entry = models.ForeignKey(
        BlacklistEntry,
        on_delete=models.CASCADE,
        related_name="votes",
        verbose_name=_("Yozuv")
    )
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blacklist_votes",
        verbose_name=_("Ovoz bergan")
    )
    is_upvote = models.BooleanField(
        verbose_name=_("Ha ovozi?")
    )
    note = models.TextField(
        blank=True,
        verbose_name=_("Izoh")
    )

    class Meta:
        verbose_name = "Qora ro'yxat ovozi"
        verbose_name_plural = "Qora ro'yxat ovozlari"
        unique_together = ["entry", "voter"]

    def __str__(self) -> str:
        return f"{self.voter} → {'+' if self.is_upvote else '-'} on {self.entry_id}"
