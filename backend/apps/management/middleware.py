"""
ManagementAccessMiddleware — "Firewall" Bittada ERP boshqaruv tizimi uchun.
"""
from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from .permissions import is_management_user
from apps.users.models import Role


# ─────────────────────────────────────────────────────────────────────────────
# Konfiguratsiyalar
# ─────────────────────────────────────────────────────────────────────────────
DASHBOARD_PREFIX: str = "/dashboard/"
API_SUBPREFIX: str = "/dashboard/api/"
LOGIN_PATH: str = "/login/"


class ManagementAccessMiddleware:
    """ERP boshqaruv tizimi uchun "Firewall" middleware."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # 1. /dashboard/ bilan boshlanmasa, o'tkazib yuborish
        if not request.path.startswith(DASHBOARD_PREFIX):
            return self.get_response(request)

        is_api_request = request.path.startswith(API_SUBPREFIX)
        user = getattr(request, "user", None)

        # 2. Anonim foydalanuvchi
        if user is None or not user.is_authenticated:
            if is_api_request:
                return JsonResponse({"detail": "Authentication required.", "code": "not_authenticated"}, status=401)
            return redirect(f"{LOGIN_PATH}?next={request.path}")

        # 3. "THE GREAT WALL" — Ruxsatlarni tekshirish
        is_admin_user = user.is_superuser or user.is_staff or user.role in {Role.ADMIN, Role.SUPER_ADMIN}
        
        # Admin bo'lmagan foydalanuvchilar uchun cheklovlar
        if not is_admin_user:
            # Ruxsat berilgan yo'llar: o'z dashboardi yoki profil tahrirlash
            is_allowed_path = (
                request.path.startswith("/dashboard/seller/") or 
                request.path.startswith("/dashboard/profile/")
            )
            
            if not is_allowed_path:
                if is_api_request:
                    return JsonResponse({"detail": "Permission denied.", "code": "permission_denied"}, status=403)
                
                # Roliga qarab o'z dashboardiga yuborish (Task 4)
                if user.is_seller or user.is_specialist or user.is_partner:
                    return redirect("seller_dashboard_home")
                
                return redirect("/")

        # 4. Management foydalanuvchisi emas (customer)
        if not is_management_user(user) and not user.is_partner and not user.is_specialist and not user.is_seller:
            if is_api_request:
                return JsonResponse({"detail": "Ruxsat etilmagan rol.", "code": "permission_denied"}, status=403)
            return redirect("/")

        return self.get_response(request)
