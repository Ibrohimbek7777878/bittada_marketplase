"""URL routes for `chat`. Mounted under `/api/v1/chat/`."""
from __future__ import annotations

from django.urls import path

from . import views

app_name = "chat"

urlpatterns: list = [
    path("direct/<str:username>/", views.direct_chat, name="direct"),
    path("room/<uuid:room_id>/", views.chat_room, name="room"),
]
