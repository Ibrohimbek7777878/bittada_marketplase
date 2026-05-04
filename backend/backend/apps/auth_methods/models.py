"""
Auth methods.

Holds:
  * `AuthMethodConfig` — admin-toggleable enable/disable for each method
    (Google, Email OTP, Phone OTP, Telegram). Lets the platform owner switch
    methods on/off without deploys.
  * `OtpCode` — short-lived one-time codes for email + phone OTP flows.
  * `SocialIdentity` — link from a User row to an external IdP subject.
  * `Session` — active refresh-token / device records for revocation.
"""
from __future__ import annotations

import secrets
import string
from datetime import timedelta

from django.db import models
from django.utils import timezone

from core.models import BaseModel


class AuthMethod(models.TextChoices):
    EMAIL_PASSWORD = "email_password", "Email + password"
    EMAIL_OTP = "email_otp", "Email OTP"
    PHONE_OTP = "phone_otp", "Phone OTP"
    GOOGLE = "google", "Google"
    TELEGRAM = "telegram", "Telegram"


class AuthMethodConfig(BaseModel):
    """One row per supported method — admin toggles `enabled` and tweaks settings."""

    method = models.CharField(max_length=24, choices=AuthMethod.choices, unique=True)
    enabled = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True, help_text="Provider-specific config.")

    class Meta:
        db_table = "auth_methods_config"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.method} ({'on' if self.enabled else 'off'})"


class OtpPurpose(models.TextChoices):
    REGISTER = "register", "Register"
    LOGIN = "login", "Login"
    RESET = "reset", "Reset password"
    VERIFY = "verify", "Verify channel"


class OtpCode(BaseModel):
    """
    Short-lived one-time code.

    `target` holds the channel address (email or +99890...).
    Codes are 6 digits, valid for 5 minutes, single-use.
    """

    target = models.CharField(max_length=160, db_index=True)
    purpose = models.CharField(max_length=12, choices=OtpPurpose.choices)
    method = models.CharField(max_length=24, choices=AuthMethod.choices)
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "auth_methods_otp"
        indexes = [models.Index(fields=["target", "purpose"])]

    @classmethod
    def generate_code(cls, length: int = 6) -> str:
        """Crypto-safe numeric code — 6 digits by default."""
        alphabet = string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def is_valid(self) -> bool:
        return self.consumed_at is None and self.expires_at > timezone.now() and self.attempts < 5

    @classmethod
    def default_ttl(cls) -> timedelta:
        return timedelta(minutes=5)


class SocialIdentity(BaseModel):
    """Maps an external IdP subject (Google sub, Telegram user_id) to a Bittada user."""

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="social_identities",
    )
    provider = models.CharField(max_length=24, choices=AuthMethod.choices)
    subject = models.CharField(max_length=200, db_index=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "auth_methods_social_identity"
        unique_together = ("provider", "subject")


class Session(BaseModel):
    """
    Active session record. Created on each successful login.

    Lets users see their active devices and revoke them. Refresh tokens are
    additionally tracked by SimpleJWT's blacklist; this row carries the UX
    metadata (device, geo, last seen).
    """

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="sessions",
    )
    method = models.CharField(max_length=24, choices=AuthMethod.choices)
    refresh_jti = models.CharField(max_length=64, unique=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    geo_country = models.CharField(max_length=2, blank=True)
    last_seen_at = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "auth_methods_session"
        ordering = ["-last_seen_at"]
