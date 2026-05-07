"""
Read queries for `chat`.

Pure functions returning querysets / dicts. No side effects, no writes.
Optimize with `select_related` / `prefetch_related` here, not in views.

Daxlsizlik eslatma: bu fayl avval faqat docstring va `from __future__`
qatoridan iborat edi. Mavjud `apps.chat.services` modulidagi yozish
funksiyalariga (get_or_create_direct_room, send_message) tegmaymiz —
faqat read funksiyalarini shu yerga qo'shamiz.
"""
from __future__ import annotations  # Type hint sintaksisi

# Type hint uchun QuerySet va Q
from django.db.models import QuerySet, Q

# Models — ChatRoom, Message
from .models import ChatRoom, Message


def get_messages(room_id, *, limit: int | None = None) -> QuerySet[Message]:
    """
    Berilgan chat xonasi bo'yicha xabarlarni qaytaradi (eskidan yangi tartibda).

    Optimallashtirish:
    - select_related: sender (FK) — har bir xabarda jo'natuvchi avatar/username

    Argumentlar:
        room_id: ChatRoom UUID
        limit: opsional — eng so'nggi N xabar uchun

    Qaytaradi:
        QuerySet[Message] — `created_at` ASC tartibda
    """
    # Asosiy queryset — xona bo'yicha filter, sender JOIN (avatar uchun profile ham)
    qs = (
        Message.objects.filter(room_id=room_id)
        .select_related("sender", "sender__profile")  # username + profile (avatars)
        .order_by("created_at")  # Eski → yangi (chat tartibi)
    )
    # Limit (so'nggi N xabar uchun, masalan polling'da)
    if limit is not None:
        # Eng oxirgilarni olish: avval reverse, slice, keyin qaytadan reverse
        qs = qs.order_by("-created_at")[:limit]
        # `qs` endi list emas, QuerySet — list() qilib reverse qilamiz
        return list(reversed(list(qs)))  # type: ignore[return-value]
    return qs


def get_room_for_user(room_id, user) -> ChatRoom | None:
    """
    Chat xonasini topadi va `user` uning ishtirokchisi ekanligini tekshiradi.

    Argumentlar:
        room_id: ChatRoom UUID
        user: User obyekti (request.user)

    Qaytaradi:
        ChatRoom (agar user ishtirokchisi bo'lsa) yoki None
    """
    try:
        # Bitta queryda: xonani topish va user ishtirokchimi tekshirish
        # `participants__id=user.id` — M2M JOIN orqali tekshirish
        room = (
            ChatRoom.objects.select_related("order")  # Order bog'liqlik (kim xaridor/sotuvchi)
            .prefetch_related("participants__profile")  # Avatar/username uchun
            .filter(pk=room_id, participants__id=user.id)
            .first()  # Birinchi mosini olish (yo'q bo'lsa None)
        )
        return room
    except (ValueError, ChatRoom.DoesNotExist):
        # ValueError — UUID format noto'g'ri bo'lsa
        return None


def get_or_create_room_for_order(order, current_user):
    """
    Buyurtma uchun chat xonasini topadi yoki yaratadi.

    `apps.chat.services.get_or_create_direct_room` ga ulanish — uni shu
    yerda thin wrapper qilamiz, chunki order'dan ikki ishtirokchi
    (customer va seller) avtomatik ajratiladi.

    Argumentlar:
        order: Order obyekti
        current_user: chat'ga kirayotgan foydalanuvchi (validation uchun)

    Qaytaradi:
        ChatRoom obyekti yoki None (agar current_user buyurtmaga aloqasi bo'lmasa).
    """
    # Permission: faqat order.customer yoki order.seller chat ocha oladi
    if current_user.id not in (order.customer_id, order.seller_id):
        return None

    # Lazy import — circular import oldini olish uchun (services chat modelini import qiladi)
    from .services import get_or_create_direct_room
    return get_or_create_direct_room(order.customer, order.seller, order=order)
