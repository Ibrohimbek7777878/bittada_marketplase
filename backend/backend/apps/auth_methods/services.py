"""
Auth flow business logic.

Each method is a small composable function so endpoints stay declarative.
Side-effects (sending email/SMS) are dispatched as Celery tasks — the
endpoint never blocks on outbound I/O.
"""
from __future__ import annotations

import hashlib

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone

from core.exceptions import DomainError, RateLimitedDomain

from apps.users.models import User
from apps.users.services import create_user_with_profile

from .models import AuthMethod, AuthMethodConfig, OtpCode, OtpPurpose


def _hash_code(code: str) -> str:
    """SHA-256 hash — codes never stored in plaintext, even short ones."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def method_enabled(method: str) -> bool:
    """Check whether a method is currently enabled by an admin."""
    cfg = AuthMethodConfig.objects.filter(method=method).first()
    return bool(cfg and cfg.enabled)


@transaction.atomic # Tranzaksiya ichida ishlashni ta'minlaydi (xato bo'lsa hamma narsa bekor bo'ladi)
def register_with_email_password( # Foydalanuvchini ro'yxatdan o'tkazish funksiyasi (rolga mos maydonlar bilan)
    *, # Faqat nomlangan argumentlarni qabul qiladi
    email: str | None = None, # Email (ixtiyoriy)
    phone: str | None = None, # Telefon (ixtiyoriy)
    password: str, # Parol (majburiy)
    first_name: str = "", # Ism (barcha rollar uchun)
    username: str | None = None, # Username (ixtiyoriy)
    role: str = "customer", # Rol (sukut bo'yicha xaridor)
    account_type: str = "individual", # Hisob turi (shaxsiy)
    professions: list[str] | None = None, # Kasblar (sotuvchilar uchun - TZ 6.3)
    company_name: str = "", # Kompaniya nomi (sotuvchilar uchun)
    experience: int | None = None, # Tajriba yillar soni (sotuvchilar uchun)
    invite_code: str = "", # Taklif kodi (ichki ta'minotchilar uchun)
) -> User: # User obyektini qaytaradi
    # Agar na email, na telefon berilgan bo'lsa, xato berish
    if not email and not phone:
        raise DomainError("Email yoki telefon raqami kiritilishi shart.")

    # Email/Parol usuli yoqilganligini tekshirish
    if email and not method_enabled(AuthMethod.EMAIL_PASSWORD):
        raise DomainError("Email orqali ro'yxatdan o'tish hozirda o'chirilgan.")
    
    # Telefon orqali ro'yxatdan o'tish usuli yoqilganligini tekshirish
    if phone and not method_enabled(AuthMethod.PHONE_OTP):
        # Bu yerda telefon/parol usuli alohida AuthMethod sifatida bo'lmagani uchun PHONE_OTP dan foydalanamiz
        pass 

    # Agar email berilgan bo'lsa va u allaqachon bazada bo'lsa
    if email and User.objects.filter(email__iexact=email).exists():
        raise DomainError("Ushbu email bilan allaqachon ro'yxatdan o'tilgan.", code="email_taken")
    
    # Agar telefon berilgan bo'lsa va u allaqachon bazada bo'lsa
    if phone and User.objects.filter(phone=phone).exists():
        raise DomainError("Ushbu telefon raqami bilan allaqachon ro'yxatdan o'tilgan.", code="phone_taken")

    # XAVFSIZLIK: admin va super_admin rollari uchun ochiq register bloklash (TZ 8.2)
    from apps.users.models import Role
    if role in {Role.ADMIN, Role.SUPER_ADMIN}: # Agar rol admin yoki super_admin bo'lsa
        raise DomainError( # Xato qaytarish
            "Admin va Super Admin rollari uchun ochiq ro'yxatdan o'tish mumkin emas. "
            "Ularni faqat createsuperuser yoki Admin Panel orqali yaratish mumkin."
        )

    # Foydalanuvchini va uning profilini yaratish
    user = create_user_with_profile(
        email=email,
        phone=phone, # Telefon raqamini ham uzatamiz
        password=password,
        username=username,
        role=role,
        account_type=account_type,
        professions=professions,
    )

    # Profilga rolga mos qo'shimcha maydonlarni yozish
    profile = user.profile # Foydalanuvchi profilini olish
    if first_name: # Agar ism berilgan bo'lsa
        profile.display_name = first_name # Profilga display_name sifatida yozish
    if company_name: # Agar kompaniya nomi berilgan bo'lsa (sotuvchilar uchun)
        profile.company_name = company_name # Profilga kompaniya nomini yozish
    if experience is not None: # Agar tajriba berilgan bo'lsa (sotuvchilar uchun)
        # Tajriba ma'lumotini bio ga qo'shish (keyinchalik alohida field bo'ladi)
        profile.bio = f"Tajriba: {experience} yil" # Profilga tajriba ma'lumotini yozish
    profile.save() # Profilni saqlash

    return user # Yaratilgan foydalanuvchini qaytarish


@transaction.atomic
def issue_otp(*, target: str, purpose: str, method: str) -> OtpCode:
    """Create a fresh OTP. Caller dispatches the delivery via tasks."""
    if not method_enabled(method):
        raise DomainError(f"{method} is disabled.")

    # Rate limit: max 3 OTPs per (target, purpose) within 5 minutes.
    recent_window = timezone.now() - OtpCode.default_ttl()
    recent = OtpCode.objects.filter(
        target=target, purpose=purpose, created_at__gte=recent_window,
    ).count()
    if recent >= 3:
        raise RateLimitedDomain("Too many OTP requests. Try later.")

    code = OtpCode.generate_code()
    otp = OtpCode.objects.create(
        target=target,
        purpose=purpose,
        method=method,
        code_hash=_hash_code(code),
        expires_at=timezone.now() + OtpCode.default_ttl(),
    )
    # Side-channel attribute used by the dispatcher Celery task; not persisted.
    otp.plain_code = code  # type: ignore[attr-defined]
    return otp


@transaction.atomic
def confirm_otp(*, target: str, code: str, purpose: str) -> OtpCode:
    """Validate a presented OTP — single-use, attempt-counted."""
    otp = (
        OtpCode.objects
        .select_for_update()
        .filter(target=target, purpose=purpose, consumed_at__isnull=True)
        .order_by("-created_at")
        .first()
    )
    if not otp:
        raise DomainError("OTP not found.", code="otp_invalid")
    if not otp.is_valid():
        raise DomainError("OTP expired or exhausted.", code="otp_invalid")

    otp.attempts += 1
    if not check_password(code, make_password(code)) or otp.code_hash != _hash_code(code):
        otp.save(update_fields=["attempts"])
        raise DomainError("OTP code mismatch.", code="otp_invalid")

    otp.consumed_at = timezone.now()
    otp.save(update_fields=["consumed_at", "attempts"])
    return otp


def seed_default_method_configs() -> None:
    """Idempotent: ensure one row per method exists. Call from a data migration."""
    for method in AuthMethod.values:
        AuthMethodConfig.objects.get_or_create(
            method=method,
            defaults={"enabled": method == AuthMethod.EMAIL_PASSWORD},
        )
