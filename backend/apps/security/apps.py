"""App config for `security`."""
from __future__ import annotations

from django.apps import AppConfig


class SecurityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.security"
    verbose_name = "Security (audit, IP, rate limit)"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
