"""Custom throttle classes used by sensitive endpoints."""
from __future__ import annotations

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthEndpointThrottle(AnonRateThrottle):
    """Tight throttle for login/register/OTP — combats credential stuffing."""
    scope = "auth"


class ContactUnlockThrottle(UserRateThrottle):
    """Cap how fast a user can spend credits on contact reveals."""
    scope = "contact"
