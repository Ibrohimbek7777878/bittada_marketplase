"""App config for `variants`."""
from __future__ import annotations

from django.apps import AppConfig


class VariantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.variants"
    verbose_name = "Variants"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
