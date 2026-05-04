"""App config for `billing`."""
from __future__ import annotations

from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.billing"
    verbose_name = "Billing & credits"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
