"""
ASGI entrypoint.

HTTP requests go through Django's ASGI handler.
WebSocket requests are routed through Channels with auth + origin validation.
This is what daphne / uvicorn serves.
"""
from __future__ import annotations

import os
import sys

# Ensure the project root (backend/) is on sys.path so that
# `apps.*`, `config.*`, and `core.*` are importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

# Lazy import — Channels routes touch the apps registry, so we must setup() first.
from apps.chat.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    ),
})
