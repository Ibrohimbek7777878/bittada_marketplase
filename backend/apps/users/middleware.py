"""
BlockCustomerAdminAccessMiddleware — Mijozlardan admin panelga kirishni cheklash.

Maqsad: role='customer' bo'lgan foydalanuvchilar Django admin panelga
(/admin/ yoki /hidden-core-database/) kira olmasligini ta'minlaydi.
Agar ular ushbu yo'llarga kirishga urinsa, ularni /profile/ sahifasiga
qaytarib yuboradi yoki 403 Forbidden javobini qaytaradi.

Joylashuvi: settings.MIDDLEWARE'da AuthenticationMiddleware'dan KEYIN,
Administrative view'lar oldin chaqirilishi kerak.
"""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect


class BlockCustomerAdminAccessMiddleware:
    """Mijozlar (customer) uchun admin panelga kirishni bloklovchi middleware."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Foydalanuvchi ma'lumotlarini olish (AuthenticationMiddleware allaqachon ishlatilgan)
        user = getattr(request, "user", None)

        # Agar foydalanuvchi autentifikatsiyalangan va role 'customer' bo'lsa
        if user is not None and user.is_authenticated and getattr(user, "role", None) == "customer":
            # So'rov yo'li admin panelga tegishli bo'lsa
            path = request.path
            # Django adminning haqiqiy joyi /hidden-core-database/ (loyiha konfiguratsiyasiga qarab)
            # Shuningdek, odatiy /admin/ ham bloklanadi (xavfsizlik qat'iyati)
            if path.startswith("/admin/") or path.startswith("/hidden-core-database/"):
                # Mijozlarni profil sahifasiga qaytarish (yoki 403 qaytarish mumkin)
                # HTTP 302 redirect
                return HttpResponseRedirect("/profile/")
                # Alternativa: 403 Forbidden
                # from django.http import HttpResponseForbidden
                # return HttpResponseForbidden("Sizda bu sahifaga kirish huquqi yo'q.")

        # Aks holda — normally proceed
        return self.get_response(request)
