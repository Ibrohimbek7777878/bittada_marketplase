"""Pytest fixtures shared across all backend tests."""
from __future__ import annotations

import pytest

from apps.users.models import Role
from apps.users.services import create_user_with_profile


@pytest.fixture
def make_user(db):  # type: ignore[no-untyped-def]
    """Factory: `make_user(role="seller")` → User."""
    counter = {"i": 0}

    def _make(*, email: str | None = None, role: str = Role.CUSTOMER, **kwargs):
        counter["i"] += 1
        return create_user_with_profile(
            email=email or f"user{counter['i']}@example.com",
            password="StrongPass!1",
            role=role,
            **kwargs,
        )

    return _make


@pytest.fixture
def customer(make_user):  # type: ignore[no-untyped-def]
    return make_user()


@pytest.fixture
def seller(make_user):  # type: ignore[no-untyped-def]
    return make_user(role=Role.SELLER, professions=["manufacturer"])
