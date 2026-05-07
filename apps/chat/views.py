"""DRF views / viewsets for `chat`."""
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from rest_framework.viewsets import ViewSet  # noqa: F401

from .models import ChatRoom
from .services import get_or_create_direct_room


@login_required
def direct_chat(request, username: str):
    User = get_user_model()
    seller = get_object_or_404(User, username=username)
    room = get_or_create_direct_room(request.user, seller)
    return redirect("chat:room", room_id=room.id)


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom.objects.prefetch_related("messages", "participants"), id=room_id)
    if not room.participants.filter(id=request.user.id).exists():
        return redirect("home")
    other_party = room.participants.exclude(id=request.user.id).first()
    return TemplateResponse(request, "chat/room.html", {
        "room": room,
        "messages": room.messages.all(),
        "other_party": other_party,
        "order": room.order,
        "page_title": getattr(other_party, "username", "Chat"),
    })
