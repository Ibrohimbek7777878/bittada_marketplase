"""App config for `chat`."""
from __future__ import annotations

from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat"
    verbose_name = "Chat"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
