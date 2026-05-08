"""
User services — write paths for core user domain.
Professionalized for Django 5 & Python 3.12 with Service/Selector pattern.
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from core.exceptions import ConflictDomain, DomainError
from .models import (
    AccountType,
    PermissionGrant,
    Profession,
    Profile,
    ProfileAvatar,
    Role,
)

User = get_user_model()
logger = logging.getLogger(__name__)

@transaction.atomic
def create_user_with_profile(
    *,
    email: str | None = None,
    phone: str | None = None,
    password: str,
    first_name: str = "",
    username: str | None = None,
    role: str = Role.CUSTOMER,
    account_type: str = AccountType.INDIVIDUAL,
    professions: list[str] | None = None,
    is_active: bool = True,
) -> User:
    """
    Creates a User and associated Profile in a single transaction.
    Professionalized for multi-step registration logic.
    """
    # Validation: Only sellers can have professions
    if professions and role not in {Role.SELLER, Role.INTERNAL_SUPPLIER}:
        raise DomainError("Faqat sotuvchilar mutaxassislik tanlashi mumkin.")

    # Validation: Profession existence
    valid_professions = {p.value for p in Profession}
    if professions:
        for p in professions:
            if p not in valid_professions:
                raise DomainError(f"Noma'lum mutaxassislik: {p}")

    # Create User
    user = User.objects.create_user(
        email=email,
        phone=phone,
        password=password,
        username=username,
        role=role,
        account_type=account_type,
        is_active=is_active,
    )

    # Create Profile
    Profile.objects.create(
        user=user,
        display_name=first_name,
        professions=professions or []
    )
    
    # Initialize Billing Wallet (TZ 15)
    from apps.billing.services import create_wallet_for_user
    create_wallet_for_user(user=user)

    logger.info(f"User created: {user.username} (ID: {user.id})")
    return user

@transaction.atomic
def update_user_last_login(user: User) -> None:
    """Updates last_login and last_seen_at in one go."""
    now = timezone.now()
    User.objects.filter(pk=user.pk).update(
        last_login=now,
        last_seen_at=now
    )

@transaction.atomic
def update_profile(*, user: User, **fields: Any) -> Profile:
    """Updates profile fields with strict role-based validation."""
    profile, _ = Profile.objects.get_or_create(user=user)

    if "professions" in fields:
        professions = fields.pop("professions")
        if not user.is_seller:
            raise DomainError("Faqat sotuvchilar mutaxassislikni o'zgartira oladi.")
        
        valid = {p.value for p in Profession}
        if any(p not in valid for p in professions):
            raise DomainError("Noto'g'ri mutaxassislik tanlandi.")
        profile.professions = professions

    for key, value in fields.items():
        if hasattr(profile, key):
            setattr(profile, key, value)

    profile.save()
    return profile

@transaction.atomic
def initiate_multi_step_login(user: User) -> dict[str, Any]:
    """
    Logic for multi-step login. 
    If 2FA is required, issues OTP. Otherwise returns success.
    """
    from apps.auth_methods.services import issue_otp
    from apps.auth_methods.models import AuthMethod, OtpPurpose

    # Logic: if user is staff or specifically enabled 2FA
    if user.is_staff or getattr(user, "is_2fa_enabled", False):
        otp = issue_otp(
            target=user.email or user.phone,
            purpose=OtpPurpose.LOGIN,
            method=AuthMethod.EMAIL_OTP if user.email else AuthMethod.PHONE_OTP
        )
        return {"step": "otp_required", "target": otp.target}
    
    return {"step": "complete"}

def mark_seen(user: User) -> None:
    """Heartbeat for last_seen_at."""
    User.objects.filter(pk=user.pk).update(last_seen_at=timezone.now())
