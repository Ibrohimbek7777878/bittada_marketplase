"""
Business logic (services) for the chat domain.
Handles room creation, message sending, and notifications.
"""
from __future__ import annotations

from django.db import transaction
from django.core.exceptions import ValidationError
from .models import ChatRoom, Message

@transaction.atomic
def get_or_create_direct_room(user1, user2, order=None) -> ChatRoom:
    """
    Ikki foydalanuvchi o'rtasidagi chat xonasini oladi yoki yangisini yaratadi.
    """
    # 1. O'z-o'ziga yozishni taqiqlash
    if user1 == user2:
        raise ValidationError("O'zingiz bilan chat yarata olmaysiz.")

    # 2. Mavjud xonani qidirish (ikkala ishtirokchi ham bo'lgan xona)
    # Eslatma: Bu sodda mantiq, katta tizimlarda ishtirokchilar sonini ham tekshirish kerak
    room = ChatRoom.objects.filter(participants=user1).filter(participants=user2)
    
    # Agar buyurtma bo'lsa, shu buyurtmaga tegishlisini qidiramiz
    if order:
        room = room.filter(order=order)
    
    room = room.first()

    # 3. Agar xona topilmasa, yangisini yaratamiz
    if not room:
        room = ChatRoom.objects.create(order=order)
        room.participants.add(user1, user2)

    return room

@transaction.atomic
def send_message(sender, room: ChatRoom, text: str, attachment=None) -> Message:
    """
    Chat xonasiga xabar yuboradi.
    """
    # 1. Yuboruvchi xona ishtirokchisi ekanligini tekshiramiz
    if not room.participants.filter(id=sender.id).exists():
        raise ValidationError("Siz bu xona ishtirokchisi emassiz.")

    # 2. Xabarni yaratamiz
    message = Message.objects.create(
        room=room,
        sender=sender,
        text=text,
        attachment=attachment
    )

    # 3. Xona yangilangan vaqtini yangilaymiz (last_message_at auto_now orqali yangilanadi)
    room.save() # update_fields ishlatilmaydi, chunki auto_now har qanday save() da ishlaydi

    # 4. Bu yerda kelgusida WebSocket orqali xabar yuborish (Daphne/Channels) mantiqi qo'shiladi
    
    return message

@transaction.atomic
def mark_messages_as_read(user, room: ChatRoom) -> int:
    """
    Xonadagi barcha xabarlarni o'qilgan deb belgilaydi (yuboruvchidan boshqalar uchun).
    """
    # User yubormagan va hali o'qilmagan xabarlarni yangilaymiz
    count = room.messages.exclude(sender=user).filter(is_read=False).update(is_read=True)
    return count
