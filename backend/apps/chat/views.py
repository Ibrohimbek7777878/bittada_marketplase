"""
Chat views — Django Templates + HTMX polling.

URL'lar (apps/chat/urls.py'dagi `template_urlpatterns`):
- /chat/order/<order_id>/   → OpenChatForOrderView (yo'naltiruvchi)
- /chat/room/<room_id>/     → ChatRoomView (asosiy chat sahifa)
- /chat/room/<room_id>/messages/ → MessagesPartialView (HTMX polling target)
- /chat/room/<room_id>/send/     → SendMessageView (HTMX POST)

Daxlsizlik: bu fayl avval faqat `from rest_framework.viewsets import ViewSet`
import qatoridan iborat edi. Mavjud kodga aralashilmagan.
"""
from __future__ import annotations  # Type hint sintaksisi

# Django imports — Templates va HTMX uchun
from django.contrib.auth.mixins import LoginRequiredMixin  # CBV uchun login required
from django.core.exceptions import PermissionDenied  # 403 javob beruvchi standart Django exception
from django.http import Http404, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.views.decorators.http import require_POST  # POST-only dekoratori
from django.utils.decorators import method_decorator  # CBV'ga dekorator qo'llash uchun

# DRF mavjud import — saqlab qo'yamiz (eski kod)
from rest_framework.viewsets import ViewSet  # noqa: F401

# Selektorlar va modellar
from .models import ChatRoom, Message
from .selectors import get_messages, get_room_for_user, get_or_create_room_for_order
from .services import send_message  # Mavjud yozish funksiyasi (chat/services.py)


class OpenChatForOrderView(LoginRequiredMixin, View):
    """
    `/chat/order/<uuid:order_id>/` — buyurtma uchun chat xonasini ochadi.

    Logika:
    - Order'ni topish, user buyer/seller ekanligini tekshirish
    - Mavjud xona bo'lsa o'sha, yo'q bo'lsa yarating
    - `/chat/room/<room_id>/` ga redirect

    Bu view'ning maqsadi — order_id'dan room_id'ga "tarjima qilish" va
    URL'da chat xonasini doim mavjud holga keltirish.
    """

    login_url = "/login/"  # Login required uchun

    def get(self, request, order_id):  # type: ignore[no-untyped-def]
        """GET: order_id orqali xona ochish va redirect."""
        # Lazy import (circular oldini olish)
        from apps.orders.models import Order
        # Order topish (yo'q bo'lsa 404)
        order = get_object_or_404(Order, pk=order_id)
        # Permission: faqat buyer yoki seller xona ocha oladi
        if request.user.id not in (order.customer_id, order.seller_id):
            return HttpResponseForbidden("Bu buyurtmaga aloqangiz yo'q.")
        # Xonani topish/yaratish (services orqali)
        room = get_or_create_room_for_order(order, request.user)
        if room is None:
            return HttpResponseForbidden("Chat xonasini yaratib bo'lmadi.")
        # Asosiy chat sahifasiga redirect
        return redirect("chat:room", room_id=room.pk)


class ChatRoomView(LoginRequiredMixin, TemplateView):
    """
    `/chat/room/<uuid:room_id>/` — asosiy chat sahifa.

    Permission: faqat ChatRoom.participants ichidagi userlar kira oladi.
    Boshqalar — 403 (vazifa talabi).
    Render: templates/chat/room.html (HTMX polling 3s).
    """

    template_name = "chat/room.html"  # Yangi yaratiladi
    login_url = "/login/"

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        ctx = super().get_context_data(**kwargs)
        room_id = kwargs.get("room_id") or self.kwargs.get("room_id")

        # Selektor: xona + permission tekshiruvi (user ishtirokchimi)
        room = get_room_for_user(room_id, self.request.user)
        if room is None:
            # Xona yo'q yoki user ishtirokchi emas — 403
            raise PermissionDenied("Bu chat xonasiga ruxsatingiz yo'q.")

        # Xabarlar (initial render)
        messages = get_messages(room_id)

        # Boshqa ishtirokchi (chat sarlavhasi uchun) — barcha participants ichidan o'zini ayri olib tashlaymiz
        other_participants = [p for p in room.participants.all() if p.id != self.request.user.id]
        other_party = other_participants[0] if other_participants else None

        # Bog'langan buyurtma (agar mavjud bo'lsa)
        order = room.order  # FK to Order; null bo'lishi mumkin

        ctx.update({
            "room": room,
            "messages": messages,
            "other_party": other_party,
            "order": order,
            "page_title": f"Chat — @{other_party.username}" if other_party else "Chat",
        })
        return ctx


class MessagesPartialView(LoginRequiredMixin, View):
    """
    `/chat/room/<uuid:room_id>/messages/` — HTMX polling target.

    Har 3 sekundda chat ro'yxat butun xabarlar fragmentini qaytaradi
    (templates/chat/message_partial.html). Faqat ishtirokchi ko'ra oladi.
    """

    login_url = "/login/"

    def get(self, request, room_id):  # type: ignore[no-untyped-def]
        """GET: barcha xabarlarni partial template sifatida qaytaradi."""
        # Permission: user xona ishtirokchimi tekshiruvi
        room = get_room_for_user(room_id, request.user)
        if room is None:
            return HttpResponseForbidden("Bu chat xonasiga ruxsatingiz yo'q.")

        # Selektor orqali xabarlar (sender + profile JOIN bilan)
        messages = get_messages(room_id)

        # Render — partial template (faqat xabarlar ro'yxati, full HTML emas)
        from django.template.loader import render_to_string
        html = render_to_string(
            "chat/message_partial.html",
            {
                "messages": messages,
                "current_user": request.user,  # Xabar "men" yoki "boshqa" ekanligini ajratish uchun
            },
            request=request,
        )
        return HttpResponse(html)


@method_decorator(require_POST, name="dispatch")  # Faqat POST so'roviga javob beradi
class SendMessageView(LoginRequiredMixin, View):
    """
    `/chat/room/<uuid:room_id>/send/` — yangi xabar yuborish (HTMX POST).

    Form: text (required), attachment (optional).
    Permission: user xona ishtirokchisi bo'lishi kerak.
    Javob: yangilangan xabarlar ro'yxati (HTMX `hx-swap` uchun).
    """

    login_url = "/login/"

    def post(self, request, room_id):  # type: ignore[no-untyped-def]
        """POST: yangi xabarni yaratish + yangilangan ro'yxatni qaytarish."""
        # Permission tekshiruvi
        room = get_room_for_user(room_id, request.user)
        if room is None:
            return HttpResponseForbidden("Bu chat xonasiga ruxsatingiz yo'q.")

        # Form ma'lumotlari
        text = request.POST.get("text", "").strip()
        attachment = request.FILES.get("attachment")  # ixtiyoriy

        # Bo'sh xabar (text yo'q VA attachment yo'q) — error
        if not text and not attachment:
            return HttpResponseBadRequest("Xabar matni yoki fayl kiritilishi kerak.")

        # services.send_message orqali yozish (atomic, validation bilan)
        try:
            send_message(sender=request.user, room=room, text=text, attachment=attachment)
        except Exception as exc:
            # services ValidationError berishi mumkin
            return HttpResponseBadRequest(str(exc))

        # Yangilangan xabarlar ro'yxatini partial sifatida qaytaramiz
        # HTMX `hx-target="#message-list"` shu HTML'ni almashtiradi
        from django.template.loader import render_to_string
        messages = get_messages(room_id)
        html = render_to_string(
            "chat/message_partial.html",
            {"messages": messages, "current_user": request.user},
            request=request,
        )
        return HttpResponse(html)


