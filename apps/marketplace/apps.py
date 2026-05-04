"""App config for `marketplace`."""
from __future__ import annotations

from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.marketplace"
    verbose_name = "Marketplace cross-cutting"

    def ready(self) -> None:  # pragma: no cover
        try:
            import apps.marketplace.signals  # noqa: F401
        except ImportError:
            pass
