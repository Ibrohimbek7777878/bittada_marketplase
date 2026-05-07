"""
Django Template Views — apps.management.

Bu view'lar HTML sahifalarni render qiladi (Sidebar tugmalari uchun).
Real-time ma'lumot (jadval, KPI, filter) AJAX/HTMX orqali
/dashboard/api/v1/... endpointlaridan keladi.

Strategiya:
- Bu view'lar minimal — faqat shablonni render qiladi va static kontekst yuboradi.
- Ma'lumotlar API'dan keladi (zamonaviy frontend uslubi).
- Permission tekshiruvi ManagementAccessMiddleware tomonidan qilinadi —
  bu view'larda qo'shimcha @login_required kerak emas.
"""
from __future__ import annotations  # Annotatsiya kelajak rejimi

from django.template.response import TemplateResponse  # Render uchun
from django.utils.translation import gettext_lazy as _

# ─────────────────────────────────────────────────────────────────────────────
# Yordamchi: ERP karkasini tanlash (HTMX / oddiy)
# ─────────────────────────────────────────────────────────────────────────────

def _erp_base(request) -> str:
    """HTMX so'rovida fragmenta-only karkas, oddiy so'rovda to'liq base_erp.html."""
    if request.headers.get("HX-Request"):  # HTMX boundary so'rov
        return "base_htmx.html"  # Faqat blok render qilinadi
    return "base_erp.html"  # To'liq sahifa (sidebar+navbar+footer)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Dashboard Index — /dashboard/
# ─────────────────────────────────────────────────────────────────────────────

def dashboard_index(request):
    """ERP bosh sahifa — sidebardan kirgandan keyingi 1-sahifa.

    Bu sahifa Mahsulotlar bo'limiga avtomatik yo'naltiradi (default landing).
    Kelajakda alohida "Welcome dashboard" qilinadi (KPI, eslatmalar va h.k.).
    """
    from django.shortcuts import redirect  # Lazy import (faqat shu funksiyada)
    return redirect("management:products_list")  # Mahsulotlar ro'yxati - default boshlang'ich nuqta


# ─────────────────────────────────────────────────────────────────────────────
# 2. Products — /dashboard/products/
# ─────────────────────────────────────────────────────────────────────────────

def products_list_view(request):
    """Mahsulotlar boshqaruvi sahifasi (to'liq UI).

    Bu view eski apps/products/views.py:product_admin_list_view bilan
    bir xil ishlaydi — daxlsizlik uchun shu yerda qaytadan emas, balki
    selectors.py orqali ishlaymiz.
    """
    from .. import management  # noqa: F401 — appearance trick (lazy chain)
    from . import selectors  # Lokal import (circular oldini olish)

    # Selector orqali rolga mos mahsulotlar ro'yxati
    products = selectors.list_products_for_management(request.user)[:25]  # Birinchi 25 ta (server-side)
    kpis = selectors.get_product_kpis()  # 3 ta KPI raqami

    context = {  # Shablon konteksti
        "base_template": _erp_base(request),  # ERP karkas
        "page_title": _("Mahsulotlar — Bittada ERP"),  # Tab nomi
        "section_key": "products",  # Sidebar'da qaysi tugma active bo'lishini bilish
        "kpis": kpis,  # KPI raqamlar
        "products": products,  # Birinchi sahifa (qolganlari API orqali yuklanadi)
        # API endpoint URL — frontend AJAX shu yerga so'rov yuboradi
        "api_url": "/dashboard/api/v1/products/",
    }
    return TemplateResponse(request, "management/products_list.html", context)  # Render


# ─────────────────────────────────────────────────────────────────────────────
# 3. Orders — /dashboard/orders/
# ─────────────────────────────────────────────────────────────────────────────

def orders_list_view(request):
    """Savdo (Sales) bo'limi — buyurtmalar ro'yxati."""
    from . import selectors

    orders = selectors.list_orders_for_management(request.user)[:25]  # Birinchi 25 ta
    kpis = selectors.get_sales_kpis()  # KPI

    context = {
        "base_template": _erp_base(request),
        "page_title": _("Savdo — Bittada ERP"),
        "section_key": "orders",  # Sidebar active marker
        "kpis": kpis,
        "orders": orders,
        "api_url": "/dashboard/api/v1/orders/",
    }
    return TemplateResponse(request, "management/orders_list.html", context)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Escrow — /dashboard/escrow/
# ─────────────────────────────────────────────────────────────────────────────

def escrow_list_view(request):
    """Escrow Fund — pul ushlangan buyurtmalar."""
    from . import selectors

    escrow_orders = selectors.list_escrow_orders(request.user)[:25]
    kpis = selectors.get_escrow_kpis()

    context = {
        "base_template": _erp_base(request),
        "page_title": _("Escrow Fund — Bittada ERP"),
        "section_key": "escrow",
        "kpis": kpis,
        "orders": escrow_orders,  # Order modeli ustida ishlaydi
        "api_url": "/dashboard/api/v1/escrow/",
    }
    return TemplateResponse(request, "management/escrow_list.html", context)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Credit Economy — /dashboard/credit/
# ─────────────────────────────────────────────────────────────────────────────

def credit_list_view(request):
    """Bittada Credit Economy bo'limi (placeholder)."""
    from . import selectors

    kpis = selectors.get_credit_kpis()  # Hozircha placeholder qiymatlar

    context = {
        "base_template": _erp_base(request),
        "page_title": _("Credit Economy — Bittada ERP"),
        "section_key": "credit",
        "kpis": kpis,
        "api_url": "/dashboard/api/v1/credit/",
    }
    return TemplateResponse(request, "management/credit_list.html", context)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Users — /dashboard/users/
# ─────────────────────────────────────────────────────────────────────────────

def users_list_view(request):
    """Foydalanuvchilar boshqaruvi (faqat admin/super_admin/staff).

    Eslatma: Middleware barcha /dashboard/* ga kirishni cheklaydi (seller ham kira oladi).
    Lekin /dashboard/users/ ga seller kira olmasligi uchun bu yerda alohida tekshiramiz.
    """
    from . import selectors
    from .permissions import IsManagementAdmin  # Faqat admin permission

    # Inline tekshiruv: seller bu sahifaga kira olmasin
    perm = IsManagementAdmin()  # Sinov uchun obyekt
    if not perm.has_permission(request, view=None):  # 403 javob
        from django.http import HttpResponseForbidden  # Lazy import
        return HttpResponseForbidden(
            f"<h1>403 — {_('Foydalanuvchilar boshqaruvi faqat administratorlar uchun.')}</h1>"
            f"<p><a href='/dashboard/'>{_('Bosh sahifaga qaytish')}</a></p>"
        )

    users = selectors.list_users_for_management()[:25]
    kpis = selectors.get_users_kpis()

    context = {
        "base_template": _erp_base(request),
        "page_title": _("Foydalanuvchilar — Bittada ERP"),
        "section_key": "users",
        "kpis": kpis,
        "users": users,
        "api_url": "/dashboard/api/v1/users/",
    }
    return TemplateResponse(request, "management/users_list.html", context)


# ─────────────────────────────────────────────────────────────────────────────
# 7. Blacklist — /dashboard/users/blacklist/
# ─────────────────────────────────────────────────────────────────────────────

def blacklist_view(request):
    """Qora ro'yxat — bloklangan foydalanuvchilar."""
    from . import selectors
    from .permissions import IsManagementAdmin

    perm = IsManagementAdmin()
    if not perm.has_permission(request, view=None):
        from django.http import HttpResponseForbidden  # Lazy import
        return HttpResponseForbidden(
            f"""<h1>403 — {_("Qora ro'yxat faqat administratorlar uchun.")}</h1>"""
            f"""<p><a href='/dashboard/'>{_("Bosh sahifaga qaytish")}</a></p>"""
        )

    blacklisted = selectors.list_blacklist_users()[:25]

    context = {
        "base_template": _erp_base(request),
        "page_title": _("Qora ro'yxat — Bittada ERP"),
        "section_key": "blacklist",
        "users": blacklisted,
        "api_url": "/dashboard/api/v1/users/blacklist/",
    }
    return TemplateResponse(request, "management/blacklist_list.html", context)
