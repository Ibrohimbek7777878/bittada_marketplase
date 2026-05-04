"""App config for `support`."""
from __future__ import annotations

from django.apps import AppConfig


class SupportConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.support"
    verbose_name = "Support"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
