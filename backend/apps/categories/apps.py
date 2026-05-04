"""App config for `categories`."""
from __future__ import annotations

from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.categories"
    verbose_name = "Categories"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
