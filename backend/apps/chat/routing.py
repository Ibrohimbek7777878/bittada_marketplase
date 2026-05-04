"""
WebSocket routes for chat.

P0 ships an empty list — `apps/chat` is fleshed out in P2 (Profiles & Chat).
Keeping the module importable now so `config.asgi` doesn't fail.
"""
from __future__ import annotations

websocket_urlpatterns: list = []
