"""App config for `seo`."""
from __future__ import annotations

from django.apps import AppConfig


class SeoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.seo"
    verbose_name = "SEO"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
