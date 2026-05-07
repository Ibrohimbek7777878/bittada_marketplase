"""
Users domain.
"""
from __future__ import annotations

import uuid
from typing import Any

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from core.models import BaseModel, TimestampedModel
from core.utils import slugify


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------
class Role(models.TextChoices):
    # Asosiy rollar
    CUSTOMER = "customer", "Customer (Xaridor)"
    SELLER = "seller", "Sotuvchi (Legacy)"
    INTERNAL_SUPPLIER = "internal_supplier", "Ichki ta'minotchi (Legacy)"
    ADMIN = "admin", "Admin"
    SUPER_ADMIN = "super_admin", "Super admin"

    # 1. Hamkorlar (Partners) - TZ §1
    PARTNER_MATERIAL = "partner_material", "Xom-ashyo hamkori"
    PARTNER_SERVICE = "partner_service", "Servis hamkori (Sug'urta/Kredit)"

    # 2. Dizayner va Ustalar (Specialists) - TZ §2
    DESIGNER_INTERIOR = "designer_interior", "Interyer dizayner"
    DESIGNER_3D = "designer_3d", "3D Dizayner"
    FIXER_MASTER = "fixer_master", "O'rnatuvchi usta (Sborka)"
    FIXER_REPAIR = "fixer_repair", "Ta'mirlash ustasi"

    # 3. Sotuvchilar (Sellers) - TZ §3
    SELLER_RETAIL = "seller_retail", "Chakana sotuvchi (Retail)"
    SELLER_MANUFACTURER = "seller_manufacturer", "Ishlab chiqaruvchi (Manufacturer)"
    SELLER_LOGISTICS = "seller_logistics", "Logistika (Dostavka)"
    SELLER_COMPONENT = "seller_component", "Furnitura va qismlar sotuvchisi"


class AccountType(models.TextChoices):
    INDIVIDUAL = "individual", "Individual"
    COMPANY = "company", "Company"


class Profession(models.TextChoices):
    """Sub-classification for sellers — unlocks portfolio fields per profession."""
    SUPPLIER = "supplier", "Supplier (yetkazib beruvchi)"
    MANUFACTURER = "manufacturer", "Manufacturer (ishlab chiqaruvchi)"
    MASTER = "master", "Master (usta)"
    DESIGNER = "designer", "Designer"


class ProfileVisibility(models.TextChoices):
    PUBLIC = "public", "Public"
    PRIVATE = "private", "Private (only chat partners)"
    HIDDEN = "hidden", "Hidden"


class ContactVisibility(models.TextChoices):
    """How a piece of contact info (phone / email / address) is exposed."""
    PUBLIC = "public", "Public"
    PAID_REVEAL = "paid", "Reveal on paid unlock"
    PRIVATE = "private", "Private"


# ---------------------------------------------------------------------------
# User manager
# ---------------------------------------------------------------------------
USERNAME_VALIDATOR = RegexValidator(
    regex=r"^[a-zA-Z0-9][a-zA-Z0-9\s_-]{2,29}$",
    message="Username 3-30 ta belgidan iborat bo'lishi kerak. Harflar, raqamlar, bo'shliq, chiziqcha va pastki chiziqcha ruxsat etiladi.",
)


# Telefon raqami uchun validator - faqat +998 bilan boshlanadigan 13 ta belgidan iborat raqamlarni qabul qiladi
PHONE_VALIDATOR = RegexValidator(
    regex=r"^\+998\d{9}$", # Regex mantiqi: +998 va undan keyin 9 ta raqam
    message="Telefon raqami '+998XXXXXXXXX' formatida bo'lishi kerak.", # Xato xabari
)

class UserManager(BaseUserManager["User"]): # Foydalanuvchilarni boshqarish klassi
    """Custom manager — email is the natural id, but username is the public handle.""" # Klass tavsifi

    use_in_migrations = True # Migratsiyalarda ishlatishga ruxsat

    def _create( # Foydalanuvchi yaratishning ichki funksiyasi
        self, # Klass nusxasi
        email: str | None = None, # Email ixtiyoriy bo'lishi mumkin (agar telefon bilan kirilsa)
        password: str | None = None, # Parol ixtiyoriy bo'linger bo'lishi mumkin
        *, # Faqat nomlangan argumentlar
        username: str | None = None, # Username ixtiyoriy
        phone: str | None = None, # Telefon raqami ixtiyoriy
        role: str = Role.CUSTOMER, # Rol - sukut bo'yicha 'customer'
        **extra: Any, # Qo'shimcha argumentlar
    ) -> "User": # User obyektini qaytaradi
        if not email and not phone: # Agar na email va na telefon berilgan bo'lsa
            raise ValueError("Email yoki telefon raqami talab qilinadi.") # Xato qaytarish
            
        if email: # Agar email berilgan bo'lsa
            email = self.normalize_email(email).lower() # Emailni normallashtirish va kichik harfga o'tkazish

        if not username: # Agar username berilgan bo'lmasa
            identifier = email if email else phone # Identifikator sifatida email yoki telefonni olish
            username = slugify(identifier.split("@")[0] if email else identifier.replace("+", "")) # Username yaratish
            
        username = slugify(username) # Username'ni tozalash (slugify)
        base = username # Asosiy username'ni saqlab qolish
        i = 0 # Takrorlanishlar sanog'i
        while self.model.objects.filter(username=username).exists(): # Agar username band bo'lsa
            i += 1 # Sanoqni oshirish
            username = f"{base}-{uuid.uuid4().hex[:6]}" # Tasodifiy qo'shimcha qo'shish
            if i > 5: # Agar 5 marta ham o'xshasa
                break # To'xtash

        user = self.model(email=email, phone=phone, username=username, role=role, **extra) # User obyektini yaratish
        if password: # Agar parol berilgan bo'lsa
            user.set_password(password) # Parolni xeshlash
        else: # Agar parol berilmagan bo'lsa
            user.set_unusable_password() # Parolsiz kirish (keyinchalik o'rnatish uchun)
        user.save(using=self._db) # Ma'lumotlar bazasiga saqlash
        return user # Yaratilgan foydalanuvchini qaytarish

    def create_user(self, email: str | None = None, password: str | None = None, **extra: Any) -> "User": # Oddiy foydalanuvchi yaratish
        extra.setdefault("role", Role.CUSTOMER) # Rolni 'customer' qilish
        extra.setdefault("is_staff", False) # Admin emasligini belgilash
        extra.setdefault("is_superuser", False) # Superadmin emasligini belgilash
        return self._create(email, password, **extra) # _create funksiyasini chaqirish

    def create_superuser(self, email: str, password: str | None = None, **extra: Any) -> "User": # Superadmin yaratish
        extra["role"] = Role.SUPER_ADMIN # Rolni superadmin qilish
        extra["is_staff"] = True # Admin panelga kirish ruxsati
        extra["is_superuser"] = True # Barcha huquqlarni berish
        extra["is_active"] = True # Akkauntni faollashtirish
        extra["email_verified_at"] = timezone.now() # Email tasdiqlangan deb belgilash
        return self._create(email, password, **extra) # _create funksiyasini chaqirish

# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class User(AbstractBaseUser, PermissionsMixin, TimestampedModel): # Foydalanuvchi modeli
    """
    Core user row.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Unikal ID (UUID)

    email = models.EmailField(unique=True, db_index=True, null=True, blank=True) # Email maydoni (ixtiyoriy)
    phone = models.CharField( # Telefon raqami maydoni
        max_length=20, # Maksimal uzunlik
        unique=True, # Unikal (takrorlanmas)
        db_index=True, # Qidiruv uchun indeks
        null=True, # Bo'sh bo'lishi mumkin (NULL)
        blank=True, # Formada bo'sh qolishi mumkin
        validators=[PHONE_VALIDATOR] # Validatsiya qo'shish
    )
    username = models.CharField( # Username maydoni
        max_length=30, # Maksimal uzunlik 30 ta belgi
        unique=True, # Unikal
        validators=[USERNAME_VALIDATOR], # Standart validator
        db_index=True, # Indeks
    )

    role = models.CharField(max_length=24, choices=Role.choices, default=Role.CUSTOMER, db_index=True) # Foydalanuvchi roli
    account_type = models.CharField( # Hisob turi (shaxsiy/kompaniya)
        max_length=12, choices=AccountType.choices, default=AccountType.INDIVIDUAL, # Tanlovlar
    )

    # Verification flags.
    is_active = models.BooleanField(default=True) # Akkaunt holati
    is_staff = models.BooleanField(default=False)  # Admin panelga ruxsat
    email_verified_at = models.DateTimeField(null=True, blank=True) # Email tasdiqlangan vaqti
    phone_verified_at = models.DateTimeField(null=True, blank=True) # Telefon tasdiqlangan vaqti
    kyc_verified_at = models.DateTimeField(null=True, blank=True) # Shaxs tasdiqlangan vaqti

    last_seen_at = models.DateTimeField(null=True, blank=True, db_index=True) # Oxirgi faollik vaqti

    USERNAME_FIELD = "email" # Kirish uchun asosiy maydon (email)
    REQUIRED_FIELDS = ["username"] # Superadmin yaratishda talab qilinadigan maydonlar

    objects = UserManager() # Menejerni bog'lash

    class Meta:
        db_table = "users_user"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["role", "is_active"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.username} <{self.email}>"

    # --- Convenience predicates --------------------------------------------
    @property
    def is_customer(self) -> bool:
        return self.role == Role.CUSTOMER

    @property
    def is_partner(self) -> bool:
        return self.role in {Role.PARTNER_MATERIAL, Role.PARTNER_SERVICE, Role.INTERNAL_SUPPLIER}

    @property
    def is_specialist(self) -> bool:
        return self.role in {Role.DESIGNER_INTERIOR, Role.DESIGNER_3D, Role.FIXER_MASTER, Role.FIXER_REPAIR}

    @property
    def is_seller(self) -> bool:
        return self.role in {
            Role.SELLER, 
            Role.SELLER_RETAIL, 
            Role.SELLER_MANUFACTURER, 
            Role.SELLER_LOGISTICS, 
            Role.SELLER_COMPONENT
        }

    @property
    def is_admin_role(self) -> bool:
        return self.role in {Role.ADMIN, Role.SUPER_ADMIN}

    @property
    def has_public_profile(self) -> bool:
        """Customers never get a public profile; others do (subject to visibility)."""
        if self.is_customer:
            return False
        profile = getattr(self, "profile", None)
        if profile is None:
            return False
        return profile.visibility == ProfileVisibility.PUBLIC


# ---------------------------------------------------------------------------
# Profile (1:1 with user, holds public info)
# ---------------------------------------------------------------------------
class Profile(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile",
    )

    # Display
    display_name = models.CharField(max_length=120, blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    stir = models.CharField(max_length=20, blank=True, null=True, help_text="STIR (INN)")
    mfo = models.CharField(max_length=20, blank=True, null=True, help_text="MFO")
    bank_account = models.CharField(max_length=50, blank=True, null=True, help_text="Hisob raqami")
    contract_number = models.CharField(max_length=50, blank=True, null=True, help_text="Shartnoma raqami")
    bio = models.TextField(blank=True, null=True)
    
    # Social/Multimedia (Step 3)
    cover_image = models.ImageField(upload_to="profiles/covers/", null=True, blank=True)
    video_intro = models.FileField(upload_to="profiles/intros/", null=True, blank=True)
    preferences = models.JSONField(default=dict, blank=True, help_text="UI/UX preferences (colors, layout, etc.)")

    # Profession parents (multi-select). Sellers only.
    professions = models.JSONField(
        default=list, blank=True,
        help_text="Subset of Profession.choices for sellers.",
    )

    # Contact info + per-field visibility.
    phones = models.JSONField(
        default=list, blank=True,
        help_text='List of {"number": "+998...", "visibility": "public|paid|private"}',
    )
    contact_email = models.EmailField(blank=True)
    contact_email_visibility = models.CharField(
        max_length=12, choices=ContactVisibility.choices, default=ContactVisibility.PAID_REVEAL,
    )
    telegram = models.CharField(max_length=64, blank=True)
    website = models.URLField(blank=True)

    # Address
    address_text = models.CharField(max_length=300, blank=True)
    geo_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geo_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Working hours: {"mon": {"open": "09:00", "close": "18:00"}, ...}
    working_hours = models.JSONField(default=dict, blank=True)

    # Visibility
    visibility = models.CharField(
        max_length=10, choices=ProfileVisibility.choices, default=ProfileVisibility.PUBLIC,
    )

    # Aggregated metrics (denormalised — recomputed by Celery).
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    profile_views = models.PositiveBigIntegerField(default=0)

    class Meta:
        db_table = "users_profile"

    def __str__(self) -> str:  # pragma: no cover
        return f"Profile<{self.user.username}>"


# ---------------------------------------------------------------------------
# Avatar gallery (max 6 per profile, see settings.BITTADA["MAX_PROFILE_AVATARS"])
# ---------------------------------------------------------------------------
class ProfileAvatar(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="avatars")
    image = models.ImageField(upload_to="profiles/avatars/")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "users_profile_avatar"
        ordering = ["order", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile"],
                condition=models.Q(is_primary=True),
                name="uniq_primary_avatar_per_profile",
            ),
        ]


# ---------------------------------------------------------------------------
# KYC documents (private, encrypted at rest at storage layer)
# ---------------------------------------------------------------------------
class KycDocument(BaseModel):
    class Kind(models.TextChoices):
        PASSPORT = "passport", "Passport / ID"
        REGISTRATION = "registration", "Company registration"
        TAX = "tax", "Tax certificate"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kyc_documents")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    file = models.FileField(upload_to="kyc/")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    note = models.TextField(blank=True)

    reviewed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "users_kyc_document"


# ---------------------------------------------------------------------------
# Permission grant (per-user override on top of role defaults)
# ---------------------------------------------------------------------------
class PermissionGrant(BaseModel):
    """
    Optional per-user permission override.

    Default permissions come from the user's role. Super Admin can grant or
    revoke specific actions on top of that. Stored as `(action_key, allowed)`
    so the matrix is data-driven and editable from the admin panel.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="permission_grants")
    action_key = models.CharField(max_length=120, db_index=True)
    allowed = models.BooleanField(default=True)
    note = models.CharField(max_length=240, blank=True)

    class Meta:
        db_table = "users_permission_grant"
        unique_together = ("user", "action_key")
