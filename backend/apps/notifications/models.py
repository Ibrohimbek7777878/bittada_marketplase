"""
TZ §21 - Notifications domain.
Email, push, in-app, Telegram notifications.
"""
from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class NotificationChannel(models.TextChoices):
    """TZ §21 - Notification kanallari"""
    IN_APP = "in_app", "Ilova ichidagi"
    EMAIL = "email", "Email"
    PUSH = "push", "Push (mobile/web)"
    TELEGRAM = "telegram", "Telegram"
    SMS = "sms", "SMS"


class NotificationType(models.TextChoices):
    """TZ §21 - Notification turlari"""
    # Order lifecycle
    ORDER_INQUIRY = "order_inquiry", "Yangi so'rov"
    ORDER_OFFER = "order_offer", "Taklif qabul qilindi"
    ORDER_PAID = "order_paid", "To'lov qilindi"
    ORDER_SHIPPED = "order_shipped", "Jo'natildi"
    ORDER_DELIVERED = "order_delivered", "Yetkazib berildi"
    ORDER_COMPLETED = "order_completed", "Buyurtma yakunlandi"
    ORDER_CANCELLED = "order_cancelled", "Buyurtma bekor qilindi"
    ORDER_DISPUTE = "order_dispute", "Bahs ochilgan"
    # Chat
    NEW_MESSAGE = "new_message", "Yangi xabar"
    # Contact/Credits
    CONTACT_UNLOCKED = "contact_unlocked", "Contact ochilgan"
    # Escrow
    ESCROW_RELEASED = "escrow_released", "Escrow sotuvchiga o'tdi"
    ESCROW_REFUNDED = "escrow_refunded", "Escrow xaridorga qaytdi"
    # System
    KYC_APPROVED = "kyc_approved", "KYC tasdiqlandi"
    KYC_REJECTED = "kyc_rejected", "KYC rad etildi"
    VERIFICATION_REMINDER = "verification_reminder", "Tasdiqlash eslatmasi"
    # Blacklist
    BLACKLIST_REPORT = "blacklist_report", "Qora ro'yxat hisoboti"
    BLACKLIST_VERIFIED = "blacklist_verified", "Qora ro'yxat tasdiqlandi"


class Notification(BaseModel):
    """
    TZ §21 - Asosiy notification modeli.
    Har bir notification bir nechta kanal orqali yuboriladi.
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Qabul qiluvchi")
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        verbose_name=_("Turi")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Sarlavha")
    )
    message = models.TextField(
        verbose_name=_("Xabar matni")
    )
    # Ilova ichidagi link
    action_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Action URL")
    )
    # Image for push/in-app
    image_url = models.URLField(
        blank=True,
        verbose_name=_("Rasm URL")
    )

    # Read status
    is_read = models.BooleanField(
        default=False,
        verbose_name=_("O'qilganmi?")
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("O'qilgan vaqti")
    )

    # Related object (generic)
    related_content_type = models.ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Related turi")
    )
    related_object_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Related ID")
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "-created_at"]),
            models.Index(fields=["notification_type", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.recipient} ← {self.title}"


class NotificationDelivery(BaseModel):
    """
    TZ §21 - Har bir kanal bo'yicha delivery status.
    Notification → bir nechta Delivery (email, push, telegram).
    """
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="deliveries",
        verbose_name=_("Notification")
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        verbose_name=_("Kanal")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Kutilmoqda"),
            ("sent", "Yuborildi"),
            ("delivered", "Yetkazildi"),
            ("failed", "Xatolik"),
            ("bounced", "Bounced"),
        ],
        default="pending",
        verbose_name=_("Holat")
    )
    # Provider response
    provider_message_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Provider message ID")
    )
    error_message = models.TextField(
        blank=True,
        verbose_name=_("Xatolik xabari")
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Yuborilgan vaqti")
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Yetkazilgan vaqti")
    )

    class Meta:
        verbose_name = "Notification delivery"
        verbose_name_plural = "Notification deliveries"
        unique_together = ["notification", "channel"]

    def __str__(self) -> str:
        return f"{self.notification} via {self.channel} ({self.status})"


class NotificationPreference(BaseModel):
    """
    TZ §21 - Foydalanuvchi notification sozlamalari.
    Har bir notification turi uchun qaysi kanallar faol.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name=_("Foydalanuvchi")
    )
    # Global toggles
    email_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Email faol?")
    )
    push_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Push faol?")
    )
    telegram_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Telegram faol?")
    )
    # Telegram chat ID
    telegram_chat_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Telegram chat ID")
    )
    # Per-type settings (JSON)
    type_settings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Turlar bo'yicha sozlamalar"),
        help_text=_("{\"order_inquiry\": {\"email\": true, \"push\": true}, ...}")
    )
    # Quiet hours
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Jim vaqt boshlanishi")
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Jim vaqt tugashi")
    )

    class Meta:
        verbose_name = "Notification sozlamasi"
        verbose_name_plural = "Notification sozlamalari"

    def __str__(self) -> str:
        return f"{self.user} preferences"
