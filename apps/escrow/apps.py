"""App config for `escrow`."""
from __future__ import annotations

from django.apps import AppConfig


class EscrowConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.escrow"
    verbose_name = "Escrow & wallet"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
