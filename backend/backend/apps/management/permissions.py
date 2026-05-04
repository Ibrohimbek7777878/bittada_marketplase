"""
Permissions for apps.management — kim Bittada ERP'ga kira oladi.

Bu modul DRF ViewSet'lar va Django views uchun yagona ruxsat tekshirish nuqtasi.
ManagementAccessMiddleware ham shu yerdagi `is_management_user()` funksiyasini ishlatadi.

Ruxsat sxemasi:
    - is_superuser=True            → kira oladi (Bittada eng yuqori darajadagi admin)
    - is_staff=True                → kira oladi (Bittada xodimi)
    - role='super_admin'           → kira oladi
    - role='admin'                 → kira oladi
    - role='seller'                → kira oladi (faqat o'z resurslariga, ViewSet'da filterlanadi)
    - boshqa hammasi               → rad etiladi (HTTP 403 yoki redirect)
"""
from __future__ import annotations  # Annotatsiya uchun

from typing import TYPE_CHECKING  # Faqat type-checker uchun importlar

from rest_framework.permissions import BasePermission  # DRF baza permission klassi

if TYPE_CHECKING:  # Runtime'da yuklanmaydigan importlar (circular avoidance)
    from django.contrib.auth.models import AbstractBaseUser  # User modeli uchun
    from rest_framework.request import Request  # DRF Request
    from rest_framework.views import APIView  # DRF View


# ─────────────────────────────────────────────────────────────────────────────
# Konstanta: ERP ga kira oladigan rollar (TextChoices'dagi qiymatlar)
# Bu konstanta middleware va permission'da bir xil ishlatiladi (DRY printsipi)
# ─────────────────────────────────────────────────────────────────────────────
MANAGEMENT_ROLES: frozenset[str] = frozenset({  # frozenset - immutable, xavfsiz
    "seller",        # Sotuvchi (o'z mahsulotlari va buyurtmalariga kiradi)
    "admin",         # Bittada admin (kompaniya darajasidagi nazorat)
    "super_admin",   # Eng yuqori daraja (hamma narsani ko'radi/o'zgartiradi)
})


def is_management_user(user) -> bool:
    """Foydalanuvchi Bittada ERP boshqaruv tizimiga kira oladimi-yo'qmi tekshiradi.

    Bu yagona haqiqat manbai (Single Source of Truth):
    - middleware.ManagementAccessMiddleware shu funksiyani chaqiradi
    - DRF IsManagementUser permission ham shu funksiyani chaqiradi
    - Django Template Views ham shu funksiyani ishlatadi (kelajakda)

    Args:
        user: request.user obyekti (anonim ham bo'lishi mumkin)

    Returns:
        True — foydalanuvchi ERP ga kira oladi
        False — kira olmaydi (anonim, customer, yoki noaniq rol)
    """
    # 1-bosqich: avval autentifikatsiya tekshirish (anonimni darhol rad etish)
    if user is None or not getattr(user, "is_authenticated", False):
        return False  # Anonim foydalanuvchi → ruxsat yo'q

    # 2-bosqich: Django'ning standart bayrog'lari (eng yuqori prioritet)
    if getattr(user, "is_superuser", False):  # Superuser har doim hamma narsaga kira oladi
        return True
    if getattr(user, "is_staff", False):  # Bittada xodimi (admin tomonidan tayinlangan)
        return True

    # 3-bosqich: TZ bo'yicha rol asosidagi tekshirish (apps.users.models.Role)
    user_role: str = getattr(user, "role", "") or ""  # role atributi yo'q bo'lsa - bo'sh string
    return user_role in MANAGEMENT_ROLES  # Ruxsatli rollar to'plamida bormi


class IsManagementUser(BasePermission):
    """DRF Permission: faqat Bittada ERP foydalanuvchilariga ruxsat beradi.

    Foydalanish (ViewSet'da):
        class ManagementProductViewSet(ModelViewSet):
            permission_classes = [IsManagementUser]
            ...

    Anonim yoki customer rad etiladi → HTTP 403 Forbidden.
    Middleware allaqachon /dashboard/api/v1/ ga kelishdan oldin tekshiradi,
    bu permission "ikkinchi himoya qatlami" sifatida ishlaydi (defense in depth).
    """

    message = "Sizda Bittada ERP boshqaruv tizimiga kirish huquqi yo'q."  # 403 javobida ko'rsatiladigan matn

    def has_permission(self, request, view) -> bool:
        """View darajasidagi tekshiruv — har bir so'rov boshida chaqiriladi."""
        return is_management_user(request.user)  # Yagona helper funksiyasiga delegatsiya

    def has_object_permission(self, request, view, obj) -> bool:
        """Object darajasidagi tekshiruv — masalan, sotuvchi faqat o'z mahsulotini ko'rsin.

        Default: agar foydalanuvchi ERP'ga kira olsa va superuser/admin bo'lsa — barchasiga ruxsat.
        Seller bo'lsa — faqat o'z resurslariga (obj.seller == user yoki obj.user == user).

        ViewSet'lar bu metodni override qilishi mumkin (masalan, OrderViewSet uchun).
        """
        if not is_management_user(request.user):  # Avval umumiy ruxsat
            return False

        # Superuser/Admin har doim hamma narsani ko'radi
        if request.user.is_superuser or request.user.is_staff:
            return True
        admin_roles: frozenset[str] = frozenset({"admin", "super_admin"})  # Yuqori darajadagi rollar
        if getattr(request.user, "role", "") in admin_roles:
            return True

        # Seller — faqat o'z obyektlariga (avtomatik tekshirish)
        # obj.seller maydoni mavjud bo'lsa - shuni solishtiramiz
        if hasattr(obj, "seller_id") and obj.seller_id == request.user.id:
            return True
        # obj.user maydoni mavjud bo'lsa (masalan, Order)
        if hasattr(obj, "user_id") and obj.user_id == request.user.id:
            return True

        return False  # Default: rad etish (xavfsiz tomon)


class IsManagementAdmin(BasePermission):
    """DRF Permission: faqat admin/super_admin/staff/superuser kira oladi (Seller emas).

    Foydalanish: Foydalanuvchilar boshqaruvi (Users), Qora ro'yxat (Blacklist)
    kabi sezgir bo'limlar uchun. Sotuvchilar bu yerga kira olmaydi.
    """

    message = "Bu bo'limga faqat administratorlar kira oladi."  # 403 matni

    def has_permission(self, request, view) -> bool:
        """Faqat admin darajasidagi foydalanuvchilar."""
        user = request.user
        if not getattr(user, "is_authenticated", False):  # Anonim → rad
            return False
        if user.is_superuser or user.is_staff:  # Tizim admini → ruxsat
            return True
        return getattr(user, "role", "") in {"admin", "super_admin"}  # Faqat admin rollar
