"""App config for `api`."""
from __future__ import annotations

from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
    verbose_name = "Public API"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
