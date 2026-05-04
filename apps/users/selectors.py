"""Read queries for users."""
from __future__ import annotations

from django.db.models import QuerySet

from .models import Profile, Role, User


def get_user_by_email(email: str) -> User | None:
    return User.objects.filter(email__iexact=email.strip()).first()


def get_user_by_username(username: str) -> User | None:
    return User.objects.filter(username__iexact=username.strip()).first()


def public_profile(username: str) -> Profile | None:
    """Profile if the user has opted into a public page; else None."""
    user = User.objects.filter(username__iexact=username).select_related("profile").first()
    if not user or user.is_customer:
        return None
    profile = getattr(user, "profile", None)
    if not profile or profile.visibility != "public":
        return None
    return profile


def sellers_qs() -> QuerySet[User]:
    """All sellers — used by listings, leaderboards."""
    return (
        User.objects
        .filter(role__in=[Role.SELLER, Role.INTERNAL_SUPPLIER], is_active=True)
        .select_related("profile")
    )
