"""App config for `integrations`."""
from __future__ import annotations

from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.integrations"
    verbose_name = "ERP/CRM integrations"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
