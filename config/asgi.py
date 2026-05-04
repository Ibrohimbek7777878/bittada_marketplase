"""
ASGI entrypoint.

HTTP requests go through Django's ASGI handler.
WebSocket requests are routed through Channels with auth + origin validation.
This is what daphne / uvicorn serves.
"""
from __future__ import annotations

import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
django.setup()

# Lazy import — Channels routes touch the apps registry, so we must setup() first.
from apps.chat.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    ),
})
