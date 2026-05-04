"""
Models for the chat domain.
Handles real-time messaging between marketplace participants.
"""
from __future__ import annotations

from django.db import models
from django.conf import settings
from core.models import BaseModel

class ChatRoom(BaseModel):
    """
    Chat xonasi (Dialog).
    Ikki kishi o'rtasidagi yozishmalarni birlashtiradi.
    """
    # Ishtirokchilar (ko'pga-ko'p bog'liqlik)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chat_rooms",
        verbose_name="Ishtirokchilar"
    )
    # Buyurtma bilan bog'liqlik (ixtiyoriy — agar chat buyurtma yuzasidan bo'lsa)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chats",
        verbose_name="Buyurtma"
    )
    # Oxirgi xabar vaqti (ro'yxatni tartiblash uchun)
    last_message_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Oxirgi xabar vaqti"
    )

    class Meta:
        verbose_name = "Chat xonasi"
        verbose_name_plural = "Chat xonalari"
        ordering = ["-last_message_at"]

    def __str__(self) -> str:
        # Xona ishtirokchilarini ko'rsatish
        return f"Chat xonasi #{self.id[:8]}"


class Message(BaseModel):
    """
    Chat xabari.
    """
    # Qaysi xonaga tegishli
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Xona"
    )
    # Yuboruvchi
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="Yuboruvchi"
    )
    # Xabar matni
    text = models.TextField(
        verbose_name="Xabar matni"
    )
    # O'qilganlik holati
    is_read = models.BooleanField(
        default=False,
        verbose_name="O'qildimi?"
    )
    # Biriktirilgan fayl (ixtiyoriy)
    attachment = models.FileField(
        upload_to="chat_attachments/%Y/%m/%d/",
        null=True,
        blank=True,
        verbose_name="Biriktirilgan fayl"
    )

    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering = ["created_at"]

    def __str__(self) -> str:
        # Xabarni qisqacha ko'rsatish
        return f"{self.sender.username}: {self.text[:20]}..."
