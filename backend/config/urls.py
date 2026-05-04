"""
Root URL configuration.

API surface lives under `/api/v1/`. Each app exposes its own urls module
that we mount with a stable prefix. The schema and admin sit at the top.

Pages (home, login, register) are rendered with Django templates.
"""
from __future__ import annotations

import os
import django.views.static
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def healthz(_request):
    """Liveness probe for load balancers — cheap, no DB hit."""
    return JsonResponse({"status": "ok"})


def api_root(_request):
    """API root - provides information about available endpoints."""
    from django.conf import settings
    return JsonResponse({
        "name": "Bittada Marketplace API",
        "version": "v1",
        "status": "running",
        "endpoints": {
            "auth": "/api/v1/auth/",
            "users": "/api/v1/users/",
            "products": "/api/v1/products/",
            "orders": "/api/v1/orders/",
            "test": "/api/v1/api/test-connection/",
        },
        "docs": "/api/docs/",  # Swagger UI manzili
        "schema": "/api/schema/",  # OpenAPI schema manzili
        # MUHIM ARXITEKTURA (2026-05-02 yangilanishi):
        # 1) Django'ning standart admin /hidden-core-database/ ga ko'chirildi (DB tekshirish uchun).
        # 2) Bittada ERP boshqaruv tizimi /dashboard/ ostida — alohida ekotizim.
        # 3) ERP API endpointlari /dashboard/api/v1/ ostida (ko'p qatlamli izolyatsiya).
        "django_admin_db": "/hidden-core-database/",  # Faqat tizim ma'muri DB darajasidagi tekshirish uchun
        "erp_dashboard": "/dashboard/",  # Bittada ERP HTML sahifalari (Sales/Escrow/Credit/Users)
        "erp_api": "/dashboard/api/v1/",  # ERP DRF API endpointlari
    })


api_v1_patterns = [
    path("auth/", include("apps.auth_methods.urls")),
    path("users/", include("apps.users.urls")),
    path("categories/", include("apps.categories.urls")),
    path("products/", include("apps.products.api_urls")),
    path("services/", include("apps.services.urls")),
    path("orders/", include("apps.orders.urls")),
    path("escrow/", include("apps.escrow.urls")),
    path("billing/", include("apps.billing.urls")),
    path("warehouse/", include("apps.warehouse.urls")),
    path("chat/", include("apps.chat.urls")),
    path("pages/", include("apps.pages.urls")),
    path("seo/", include("apps.seo.urls")),
    path("support/", include("apps.support.urls")),
    path("blacklist/", include("apps.blacklist.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("marketplace/", include("apps.marketplace.urls")),
    path("integrations/", include("apps.integrations.urls")),
    path("showroom/", include("apps.showroom.urls")),
    path("media/", include("apps.media.urls")),
    path("", include("apps.api.urls")),  # Test & System Health endpoints
]

# Template URL patterns (HTML pages)
template_patterns = [
    path("", include("apps.products.urls")),  # Home, shop, product pages
    path("showroom/", include("apps.showroom.urls")), # 3D Showroom page
    path("services/", include("apps.services.urls", namespace="services")), # Services module
]

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),  # Tilni o'zgartirish uchun
    path("healthz", healthz, name="healthz"),
    path("api/v1/", api_root, name="api-root"),
    path("api/v1/", include((api_v1_patterns, "api"), namespace="v1")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Sahifalar uchun til prefixlari bilan yo'llar (/uz/, /ru/, /en/)
urlpatterns += i18n_patterns(
    path("hidden-core-database/login/", RedirectView.as_view(url="/login/", query_string=True, permanent=False)),
    path("hidden-core-database/logout/", RedirectView.as_view(url="/logout/", query_string=False, permanent=False)),
    path("hidden-core-database/", admin.site.urls),
    path("dashboard/api/v1/", include("apps.management.api_urls")),
    path("dashboard/", include(("apps.management.urls", "management"), namespace="mgmt")),
    path("", include(template_patterns)),
    prefix_default_language=True,
)

if settings.DEBUG: # Agar debug rejimi yoqilgan bo'lsa
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Media fayllar (+rasmlar)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Statik fayllar (CSS, JS)
