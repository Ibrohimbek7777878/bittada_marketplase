"""App config for `warehouse`."""
from __future__ import annotations

from django.apps import AppConfig


class WarehouseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.warehouse"
    verbose_name = "Warehouse"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
