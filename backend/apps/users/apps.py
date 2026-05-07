"""App config for `users`."""
from __future__ import annotations

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    verbose_name = "Users & profiles"

    def ready(self) -> None:  # pragma: no cover
        import apps.users.signals  # noqa: F401

