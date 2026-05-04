"""User-domain permissions."""
from __future__ import annotations

from rest_framework.permissions import BasePermission


class CanEditOwnProfile(BasePermission):
    """Only the profile owner may PATCH their profile."""

    def has_object_permission(self, request, view, obj) -> bool:  # type: ignore[no-untyped-def]
        return bool(request.user.is_authenticated and obj.user_id == request.user.id)
