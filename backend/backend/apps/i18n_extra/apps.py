"""App config for `i18n_extra`."""
from __future__ import annotations

from django.apps import AppConfig


class I18nExtraConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.i18n_extra"
    verbose_name = "Extra languages / AI text"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
