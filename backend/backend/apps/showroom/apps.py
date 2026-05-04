"""App config for `showroom`."""
from __future__ import annotations

from django.apps import AppConfig


class ShowroomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.showroom"
    verbose_name = "3D Showroom"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
