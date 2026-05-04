"""
User services — write paths.

The auth flow (registration / login) lives in `apps.auth_methods` since it
spans multiple methods (email, OAuth, OTP). This module owns profile and
permission mutations only.
"""
from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from core.exceptions import ConflictDomain, DomainError

from .models import (
    AccountType,
    PermissionGrant,
    Profession,
    Profile,
    ProfileAvatar,
    Role,
    User,
)

import hashlib
import hmac


def verify_telegram_hash(*, auth_data: dict[str, Any], bot_token: str) -> bool:
    """
    Verify Telegram Login Widget data hash.
    TZ requirement: Verify telegram hash in users/services.py
    """
    check_hash = auth_data.pop('hash', None)
    if not check_hash:
        return False

    # Create data_check_string
    data_list = []
    for key, value in sorted(auth_data.items()):
        if value is not None:
            data_list.append(f"{key}={value}")
    data_check_string = "\n".join(data_list)

    # Calculate secret_key
    secret_key = hashlib.sha256(bot_token.encode()).digest()

    # Calculate HMAC-SHA256
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return hmac_hash == check_hash


@transaction.atomic # Tranzaksiya xavfsizligini ta'minlash
def create_user_with_profile( # Foydalanuvchi va profilni birgalikda yaratish
    *, # Faqat nomlangan argumentlar
    email: str | None = None, # Email (ixtiyoriy)
    phone: str | None = None, # Telefon (ixtiyoriy)
    password: str, # Parol (majburiy)
    username: str | None = None, # Username (ixtiyoriy)
    role: str = Role.CUSTOMER, # Rol (sukut bo'yicha xaridor)
    account_type: str = AccountType.INDIVIDUAL, # Hisob turi (shaxsiy)
    professions: list[str] | None = None, # Kasblar (sotuvchilar uchun)
) -> User: # User obyektini qaytaradi
    """Create a user and the empty Profile row in a single transaction.""" # Funksiya tavsifi
    
    # Sotuvchi bo'lmagan foydalanuvchilar kasb tanlay olmasligini tekshirish
    if professions and role not in {Role.SELLER, Role.INTERNAL_SUPPLIER}:
        raise DomainError("Faqat sotuvchilar kasblarni tanlashi mumkin.")

    # Kasblar mavjudligini tekshirish
    valid_professions = {p.value for p in Profession}
    for p in professions or []:
        if p not in valid_professions:
            raise DomainError(f"Noma'lum kasb: {p}")

    # Foydalanuvchini yaratish
    user = User.objects.create_user(
        email=email,
        phone=phone, # Telefon raqamini uzatish
        password=password,
        username=username,
        role=role,
        account_type=account_type,
    )
    
    # Foydalanuvchi uchun bo'sh profil yaratish
    Profile.objects.create(user=user, professions=professions or [])
    
    # --- YANGI: Foydalanuvchi uchun hamyon (Wallet) yaratish (TZ 14) ---
    from apps.billing.services import create_wallet_for_user # Circular import oldini olish uchun shu yerda import qilamiz
    create_wallet_for_user(user=user) # Hamyon yaratish funksiyasini chaqiramiz
    
    # -----------------------------------------------------------------

    return user # Yaratilgan foydalanuvchini qaytarish


@transaction.atomic
def update_profile(*, user: User, **fields: Any) -> Profile:
    """Update profile fields. Validates role-specific constraints."""
    profile, _ = Profile.objects.get_or_create(user=user)

    professions = fields.pop("professions", None)
    if professions is not None:
        if not user.is_seller:
            raise DomainError("Only sellers can set professions.")
        valid = {p.value for p in Profession}
        bad = [p for p in professions if p not in valid]
        if bad:
            raise DomainError(f"Unknown profession(s): {', '.join(bad)}")
        profile.professions = professions

    for key, value in fields.items():
        if not hasattr(profile, key):
            continue  # silently ignore unknown keys; serializer is the gate
        setattr(profile, key, value)

    profile.save()
    return profile


@transaction.atomic
def set_primary_avatar(*, user: User, avatar_id: str) -> ProfileAvatar:
    profile = user.profile
    try:
        avatar = profile.avatars.get(id=avatar_id)
    except ProfileAvatar.DoesNotExist as exc:
        raise DomainError("Avatar not found.") from exc

    profile.avatars.update(is_primary=False)
    avatar.is_primary = True
    avatar.save(update_fields=["is_primary"])
    return avatar


@transaction.atomic
def grant_permission(
    *, target: User, action_key: str, allowed: bool = True, note: str = "",
    actor: User | None = None,
) -> PermissionGrant:
    """Per-user permission override (super_admin only — caller enforces this)."""
    if actor and actor.role != Role.SUPER_ADMIN:
        raise DomainError("Only super_admin can edit permission grants.", code="permission_denied")
    grant, created = PermissionGrant.objects.update_or_create(
        user=target,
        action_key=action_key,
        defaults={"allowed": allowed, "note": note},
    )
    if not created and grant.allowed == allowed:
        raise ConflictDomain("No change.")
    return grant


def mark_seen(user: User) -> None:
    """Touch `last_seen_at` — called by middleware on each authenticated request."""
    User.objects.filter(pk=user.pk).update(last_seen_at=timezone.now())
