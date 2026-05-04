"""App config for `orders`."""
from __future__ import annotations

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orders"
    verbose_name = "Orders"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
