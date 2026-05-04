"""App config for `blacklist`."""
from __future__ import annotations

from django.apps import AppConfig


class BlacklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.blacklist"
    verbose_name = "Blacklist"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
