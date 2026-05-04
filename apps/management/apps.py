"""AppConfig for apps.management — Bittada ERP boshqaruv ekotizimi."""
from __future__ import annotations  # Kelajakdagi annotatsiyalar uchun (PEP 563)

from django.apps import AppConfig  # Django'ning standart AppConfig bazasi


class ManagementConfig(AppConfig):
    """Bittada ERP — alohida boshqaruv tizimi (Sales/Escrow/Credit/Users)."""

    default_auto_field = "django.db.models.BigAutoField"  # PK turi (loyiha standarti)
    name = "apps.management"  # To'liq import yo'li (settings.INSTALLED_APPS uchun)
    label = "management"  # Django ichidagi qisqa label (admin/migration uchun)
    verbose_name = "Bittada ERP — Boshqaruv tizimi"  # Inson o'qiy oladigan nom
