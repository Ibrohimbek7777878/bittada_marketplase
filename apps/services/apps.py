"""App config for `services`."""
from __future__ import annotations

from django.apps import AppConfig


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.services"
    verbose_name = "Services"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
