"""App config for `pages`."""
from __future__ import annotations

from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    verbose_name = "CMS pages"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
