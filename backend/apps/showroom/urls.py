"""URL routes for `showroom` — Django Templates.

Daxlsizlik eslatma: mavjud `urlpatterns` (3D Showroom) o'zgartirilmagan.
Yangi `portfolio_urlpatterns` ro'yxati qo'shildi — `config/urls.py` orqali
`/portfolio/` prefiksiga ulanadi (alohida namespace="portfolio").

Ikki ro'yxat:
  - urlpatterns: /showroom/ ostida (mavjud showroom_view)
  - portfolio_urlpatterns: /portfolio/ ostida (yangi PortfolioDetailView, PortfolioEditView)
"""
from __future__ import annotations

from django.urls import path
from .views import showroom_view, PortfolioEditView  # PortfolioEditView shu app'da
# PortfolioDetailView vazifa talabi bo'yicha apps/services/views.py'da
from apps.services.views import PortfolioDetailView

# Mavjud /showroom/ URL'lari (o'zgartirilmagan)
urlpatterns: list = [
    path("", showroom_view, name="showroom"),
]


# === YANGI: /portfolio/ URL'lari ===
# config/urls.py'dagi template_patterns'ga qo'shiladi.
# MUHIM: edit/ aniq path birinchi turishi kerak (top-down match), aks holda
# `<str:username>/` "edit" username ni qabul qilib oladi va EditView ishlamaydi.
portfolio_urlpatterns = [
    # /portfolio/edit/  →  PortfolioEditView (LoginRequired + seller)
    path("edit/", PortfolioEditView.as_view(), name="edit"),
    # /portfolio/<username>/  →  PortfolioDetailView (public, owner uchun "Tahrirlash" tugmasi)
    path("<str:username>/", PortfolioDetailView.as_view(), name="detail"),
]
