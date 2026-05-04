"""App config for `notifications`."""
from __future__ import annotations

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    verbose_name = "Notifications"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
