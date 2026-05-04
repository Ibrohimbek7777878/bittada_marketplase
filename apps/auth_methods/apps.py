"""App config for `auth_methods`."""
from __future__ import annotations

from django.apps import AppConfig


class AuthMethodsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth_methods"
    verbose_name = "Auth methods (JWT, OAuth, OTP)"

    def ready(self) -> None:  # pragma: no cover
        # Import signals here if/when we add them.
        return None
