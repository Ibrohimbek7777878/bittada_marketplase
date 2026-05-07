from __future__ import annotations

from django.utils import translation
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.users.models import User

def get_dashboard_url(user: User) -> str:
    """
    Returns the appropriate dashboard URL for a user based on their role.
    Each of the 10 professional roles gets routed to the correct dashboard section.
    """
    lang = translation.get_language() or 'uz'

    # 1. Staff and Superusers → Command Center
    if user.is_staff or user.is_superuser:
        return f"/{lang}/dashboard/"

    role = getattr(user, 'role', 'customer')

    # 2. Customers → Personal Profile
    if role == 'customer':
        return f"/{lang}/profile/"

    # 3. Logistika (Dostavchik) → Logistics dashboard
    if role == 'seller_logistics':
        return f"/{lang}/dashboard/my-products/"

    # 4. Sellers (all types) → Seller dashboard
    if role in ('seller', 'seller_retail', 'seller_manufacturer', 'seller_component'):
        return f"/{lang}/dashboard/my-products/"

    # 5. Specialists (Designers, Masters) → Profile/Portfolio
    if role in ('designer_interior', 'designer_3d', 'fixer_master', 'fixer_repair'):
        return f"/{lang}/profile/"

    # 6. Partners → Dashboard
    if role in ('partner_material', 'partner_service', 'internal_supplier'):
        return f"/{lang}/dashboard/"

    # Default fallback
    return f"/{lang}/profile/"
