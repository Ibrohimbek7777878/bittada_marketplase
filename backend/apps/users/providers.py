"""Provider directory selectors.

A "provider" is any registered user with a public profile that can offer
products, services, or portfolio work — masters, designers, installers,
manufacturers, suppliers, and individual sellers. The directory powers
``/services/`` (provider index) and is read-only.

These functions are pure: they return querysets, never write.
"""
from __future__ import annotations

from django.db.models import Count, Prefetch, Q, QuerySet

from apps.services.models import Service
from apps.showroom.models import PortfolioItem

from .models import Profession, Profile, ProfileVisibility, Role, User


# Registered roles that may appear in the public provider directory. We
# intentionally exclude admin / super_admin (internal) and customers.
_PROVIDER_ROLES = (Role.SELLER, Role.INTERNAL_SUPPLIER)


def list_providers(
    *,
    profession: str | None = None,
    role: str | None = None,
    search: str | None = None,
    only_with_content: bool = False,
) -> QuerySet[User]:
    """Return active users that should appear on the provider directory.

    Filters:
        profession: one of ``Profession.values`` — narrows to users whose
            profile lists that profession.
        role: one of ``Role.values`` — defaults to seller/internal_supplier.
        search: case-insensitive match against username, display_name,
            company_name, address.
        only_with_content: when True, only include users who have at least
            one published product, service, or portfolio item. The default
            (False) is permissive so a freshly-registered seller still
            appears.
    """
    qs = (
        User.objects.filter(is_active=True, role__in=_PROVIDER_ROLES)
        .select_related("profile")
        .prefetch_related(
            Prefetch(
                "profile__avatars",
                queryset=Profile._meta.get_field("avatars").related_model.objects.order_by(
                    "-is_primary", "order"
                ),
            )
        )
        # Hide profiles the user explicitly took down. PRIVATE still shows
        # because the listing is itself a public surface.
        .exclude(profile__visibility=ProfileVisibility.HIDDEN)
        .annotate(
            product_count=Count("products", distinct=True),
            service_count=Count("services", distinct=True),
            portfolio_count=Count("portfolio_items", distinct=True),
        )
    )

    if role:
        qs = qs.filter(role=role)

    if profession:
        # JSONField list contains check — works on both PostgreSQL and SQLite
        # because Django translates ``contains`` for JSONField.
        qs = qs.filter(profile__professions__contains=[profession])

    if search:
        term = search.strip()
        if term:
            qs = qs.filter(
                Q(username__icontains=term)
                | Q(profile__display_name__icontains=term)
                | Q(profile__company_name__icontains=term)
                | Q(profile__address_text__icontains=term)
            )

    if only_with_content:
        qs = qs.filter(
            Q(product_count__gt=0)
            | Q(service_count__gt=0)
            | Q(portfolio_count__gt=0)
        )

    return qs.order_by("-profile__rating", "-profile__review_count", "-created_at")


def profession_facets() -> list[dict]:
    """Return profession choices with counts, for the directory filter chip bar."""
    return [
        {"value": value, "label": label}
        for value, label in Profession.choices
    ]
