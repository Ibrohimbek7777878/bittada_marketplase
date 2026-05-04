"""Smoke tests for user creation."""
from __future__ import annotations

import pytest
from django.db import IntegrityError

from apps.users.models import AccountType, Profile, Role, User
from apps.users.services import create_user_with_profile

pytestmark = pytest.mark.django_db


def test_create_customer_user_creates_profile() -> None:
    user = create_user_with_profile(email="a@example.com", password="StrongPass!1")
    assert user.role == Role.CUSTOMER
    assert user.account_type == AccountType.INDIVIDUAL
    assert Profile.objects.filter(user=user).exists()


def test_email_is_unique() -> None:
    create_user_with_profile(email="dup@example.com", password="StrongPass!1")
    with pytest.raises(IntegrityError):
        User.objects.create_user(email="DUP@example.com", password="StrongPass!1")


def test_seller_can_have_professions() -> None:
    user = create_user_with_profile(
        email="m@example.com",
        password="StrongPass!1",
        role=Role.SELLER,
        professions=["manufacturer", "supplier"],
    )
    assert sorted(user.profile.professions) == ["manufacturer", "supplier"]


def test_customer_cannot_have_professions() -> None:
    from core.exceptions import DomainError
    with pytest.raises(DomainError):
        create_user_with_profile(
            email="c@example.com",
            password="StrongPass!1",
            professions=["manufacturer"],
        )
