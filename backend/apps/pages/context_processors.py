from apps.pages.models import PageContent


def cms_content(request):
    """
    Dinamik kontentni barcha templatelarga uzatish.
    Ishlatilishi: {{ cms.nav_home }}, {{ nav_categories.furniture }}
    """
    lang = getattr(request, 'LANGUAGE_CODE', 'uz')
    contents = PageContent.objects.filter(language=lang)

    cms_dict = {}
    for item in contents:
        cms_dict[item.key] = item.value

    # ── Nav categories for the Mega Menu ──────────────────────────────────
    try:
        from apps.products.models import Category, ProductType

        furniture_cats = list(
            Category.objects
            .filter(
                parent__isnull=True,
                is_active=True,
                product_type_filter=ProductType.STANDARD,
            )
            .values('name_uz', 'slug')
            .order_by('lft')[:8]
        )
        mfg_cats = list(
            Category.objects
            .filter(
                parent__isnull=True,
                is_active=True,
                product_type_filter=ProductType.MANUFACTURING,
            )
            .values('name_uz', 'slug')
            .order_by('lft')[:6]
        )
    except Exception:
        furniture_cats = []
        mfg_cats = []

    return {
        'cms': cms_dict,
        'nav_categories': {
            'furniture': furniture_cats,
            'manufacturing': mfg_cats,
        },
    }


def oauth_settings(request):
    """Add OAuth client IDs to template context."""
    from django.conf import settings
    return {
        'GOOGLE_CLIENT_ID': getattr(settings, 'GOOGLE_CLIENT_ID', ''),
        'TELEGRAM_BOT_ID': getattr(settings, 'TELEGRAM_BOT_ID', ''),
        'TELEGRAM_BOT_USERNAME': getattr(settings, 'TELEGRAM_BOT_USERNAME', ''),
    }
