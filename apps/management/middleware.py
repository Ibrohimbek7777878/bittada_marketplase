"""
ManagementAccessMiddleware — "Firewall" Bittada ERP boshqaruv tizimi uchun.

Maqsad: /dashboard/... yo'llariga har qanday ruxsatsiz so'rov darhol bizning
ERP login sahifasiga (/login/?next=...) yoki "ruxsat yo'q" javobiga uchrasin.
Django'ning quruq login formasi yoki 404 sahifasi hech qachon ko'rinmaydi.

Joylashuvi: settings.MIDDLEWARE'da AuthenticationMiddleware'dan KEYIN bo'lishi shart
(chunki request.user'ga ehtiyoji bor).

Mantiq:
    1. So'rov yo'li /dashboard/ bilan boshlanmasa — middleware o'tkazib yuboradi (passthrough).
    2. Yo'l /dashboard/... bo'lsa va foydalanuvchi anonim — /login/?next=<path> ga redirect.
    3. Autentifikatsiyalangan, lekin ruxsati yo'q (customer) — /login/?error=no_access ga redirect.
    4. Aks holda — so'rov view'ga o'tkaziladi.

Istisno: /dashboard/api/... yo'llari — DRF o'zining 403 javobini qaytaradi (HTML emas).
"""
from __future__ import annotations  # Annotatsiya kelajak rejimida

from typing import Callable  # Get_response signaturesi uchun

from django.http import HttpRequest, HttpResponse, JsonResponse  # Tip va JSON 403 uchun
from django.shortcuts import redirect  # 302 redirect helper
from django.urls import reverse  # URL nom orqali yo'lni topish (kerak bo'lsa)

from .permissions import is_management_user  # Yagona ruxsat tekshiruvchi


# ─────────────────────────────────────────────────────────────────────────────
# Konfiguratsiyalar (settings ni o'qish o'rniga shu yerda statik)
# ─────────────────────────────────────────────────────────────────────────────
DASHBOARD_PREFIX: str = "/dashboard/"  # Boshqaruv tizimi URL prefiksi (HTML va API)
API_SUBPREFIX: str = "/dashboard/api/"  # API yo'llari (JSON javob beradi)
LOGIN_PATH: str = "/login/"  # Bizning ERP login sahifasi (Django default emas)


class ManagementAccessMiddleware:
    """ERP boshqaruv tizimi uchun "Firewall" middleware.

    Django'ning standart middleware sxemasiga muvofiq:
    - __init__(get_response): bir marta serverni ishga tushirishda chaqiriladi
    - __call__(request): har bir HTTP so'rov uchun chaqiriladi
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Middleware yaratish (server start payti)."""
        self.get_response = get_response  # Keyingi middleware/view chaqiruvchi

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Har bir HTTP so'rovni qayta ishlash."""
        # ─── 1-qadam: yo'l /dashboard/ bilan boshlanmasa, passthrough ────────
        if not request.path.startswith(DASHBOARD_PREFIX):  # Boshqaruv yo'li emas
            return self.get_response(request)  # Hech narsa qilmasdan o'tkazib yuborish

        # ─── 2-qadam: API so'rovi (JSON) yoki HTML — bu farqi muhim ─────────
        is_api_request = request.path.startswith(API_SUBPREFIX)  # /dashboard/api/...
        # API uchun JSON 401/403, HTML uchun /login/ ga redirect

        # ─── 3-qadam: foydalanuvchi ruxsatini tekshirish ────────────────────
        user = getattr(request, "user", None)  # AuthenticationMiddleware allaqachon ishlatdi

        if user is None or not user.is_authenticated:  # Anonim foydalanuvchi
            if is_api_request:  # API so'rovi → JSON 401
                return JsonResponse(
                    {  # JSON javob tanasi
                        "detail": "Authentication required.",  # DRF uslubidagi xato
                        "code": "not_authenticated",  # Mashinada o'qish uchun kod
                    },
                    status=401,  # HTTP 401 Unauthorized
                )
            # HTML so'rovi → bizning login sahifaga redirect (next bilan)
            return redirect(f"{LOGIN_PATH}?next={request.path}")  # /login/?next=/dashboard/...

        if not is_management_user(user):  # Autentifikatsiyalangan, lekin huquqi yo'q
            if is_api_request:  # API → JSON 403
                return JsonResponse(
                    {
                        "detail": "Sizda Bittada ERP boshqaruv tizimiga kirish huquqi yo'q.",  # UZ matn
                        "code": "permission_denied",  # Kod
                    },
                    status=403,  # HTTP 403 Forbidden
                )
            # HTML → login sahifaga "huquq yo'q" xabari bilan
            return redirect(f"{LOGIN_PATH}?error=no_access&next={request.path}")  # Login sahifa o'zi error'ni o'qiydi

        # ─── 4-qadam: ruxsat berilgan, view'ga o'tkazish ────────────────────
        return self.get_response(request)  # Keyingi bosqichga uzatish (view yoki keyingi MW)
