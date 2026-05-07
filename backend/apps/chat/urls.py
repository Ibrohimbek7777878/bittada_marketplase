"""URL routes for `chat`.

Daxlsizlik eslatma: mavjud `urlpatterns` (DRF API uchun, ammo bo'sh edi)
saqlanib qoldi. Yangi `template_urlpatterns` ro'yxati qo'shildi —
`config/urls.py` orqali `/chat/...` prefiksiga ulanadi (i18n_patterns ichida).
"""
from __future__ import annotations

from django.urls import path

from . import views

app_name = "chat"  # Namespace: `{% url 'chat:room' room_id=... %}`

# === Mavjud DRF URL'lar (bo'sh, lekin saqlanadi — `/api/v1/chat/`) ===
urlpatterns: list = [
    # path("", views.SomeView.as_view(), name="some"),
]


# === YANGI: Template URL'lar — /chat/... ===
# config/urls.py'dagi template_patterns'ga qo'shiladi.
template_urlpatterns = [
    # Order id orqali chat ochish (xonani avtomatik topadi/yaratadi)
    # /chat/order/<uuid:order_id>/  → /chat/room/<uuid:room_id>/ ga redirect
    path("chat/order/<uuid:order_id>/", views.OpenChatForOrderView.as_view(), name="open_for_order"),

    # Asosiy chat sahifa
    # /chat/room/<uuid:room_id>/
    path("chat/room/<uuid:room_id>/", views.ChatRoomView.as_view(), name="room"),

    # HTMX polling target — har 3s chaqiriladi, partial xabarlar HTML qaytaradi
    # /chat/room/<uuid:room_id>/messages/
    path("chat/room/<uuid:room_id>/messages/", views.MessagesPartialView.as_view(), name="messages"),

    # HTMX POST — yangi xabar yuborish
    # /chat/room/<uuid:room_id>/send/
    path("chat/room/<uuid:room_id>/send/", views.SendMessageView.as_view(), name="send"),
]
