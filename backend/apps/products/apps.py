"""App config for `products`."""
from __future__ import annotations

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.products"
    verbose_name = "Products"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
