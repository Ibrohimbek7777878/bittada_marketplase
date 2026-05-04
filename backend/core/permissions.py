"""
Reusable DRF permission classes.

Per-app permissions live in `apps/<name>/permissions.py`; common ones are here.
"""
from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Anyone can read; only the owner can mutate."""

    def has_object_permission(self, request, view, obj) -> bool:  # type: ignore[no-untyped-def]
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "owner", None) or getattr(obj, "user", None) or getattr(obj, "created_by", None)
        return bool(owner and request.user.is_authenticated and owner == request.user)


class IsSeller(BasePermission):
    """Restrict to seller / internal_supplier roles."""

    message = "Only sellers can perform this action."

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        user = request.user
        return bool(user.is_authenticated and user.role in {"seller", "internal_supplier"})


class IsAdminRole(BasePermission):
    """Bittada staff (admin / super_admin)."""

    message = "Admin role required."

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        user = request.user
        return bool(user.is_authenticated and user.role in {"admin", "super_admin"})


class IsSuperAdmin(BasePermission):
    """Highest privilege — platform owner."""

    message = "Super admin role required."

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        return bool(request.user.is_authenticated and request.user.role == "super_admin")


class ReadOnlyForCustomer(BasePermission):
    """Customers read; sellers/admins can mutate."""

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user.is_authenticated and user.role != "customer")
