"""App config for `analytics`."""
from __future__ import annotations

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics"
    verbose_name = "Analytics"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
