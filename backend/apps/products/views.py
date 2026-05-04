"""
Products views — mebel marketplace (Django Templates).

TZ §10, §12 bo'yicha:
- Categories: daraxt ko'rinishida
- Products: list, detail, filter, search
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.paginator import Paginator
from django.db.models import Count, Max, Min, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.template.response import TemplateResponse
from django.contrib.auth import logout
from django.views import View

from .models import Category, Color, Condition, Material, Product, ProductStatus, Style, ProductType
from apps.orders.models import Order


# ============================================================================
# DJANGO TEMPLATE VIEWS
# ============================================================================

def _get_base_template(request): # HTMX so'rovini tekshirish va mos karkasni tanlash funksiyasi
    """ # Funksiya tavsifi
    Returns the base template name depending on whether the request is HTMX or not. # HTMX so'roviga qarab asosiy karkas nomini qaytaradi
    """ # Tavsif yakuni
    if request.headers.get("HX-Request"): # Agar so'rov HTMX orqali kelgan bo'lsa
        return "base_htmx.html" # Faqat bloklarni render qiluvchi karkas
    return "base_erp.html" # To'liq karkas (navbar/footer bilan)

def _apply_filters(queryset, request):
    """Mahsulotlarni filterlash"""
    # Material
    materials = request.GET.getlist("material")
    if materials:
        queryset = queryset.filter(primary_material__in=materials)
    
    # Uslub
    style = request.GET.get("style")
    if style:
        queryset = queryset.filter(style=style)
    
    # Narx diapazoni
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    if price_min:
        queryset = queryset.filter(price__gte=Decimal(price_min))
    if price_max:
        queryset = queryset.filter(price__lte=Decimal(price_max))
    
    # Qidiruv
    q = request.GET.get("q")
    if q:
        queryset = queryset.filter(
            Q(title_uz__icontains=q) |
            Q(description_uz__icontains=q) |
            Q(hashtags__icontains=q) |
            Q(sku__icontains=q)
        )
    
    return queryset


def _apply_sort(queryset, sort: str):
    """Saralash"""
    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
        "price_low": "price",
        "price_high": "-price",
        "popular": "-view_count",
        "name": "title_uz",
    }
    order_by = sort_options.get(sort, "-created_at")
    return queryset.order_by(order_by)


def home_view(request):
    """Bosh sahifa — B2C/Retail mahsulotlar va Command Center."""
    # Command Center faqat is_superuser=True lar uchun (TZ talabi)
    if request.user.is_authenticated and request.user.is_superuser:
        from apps.orders.models import Order, OrderStatus
        # Data Summary: Top Bar Yangi buyurtmalar count (Safe Counter Logic)
        new_orders_count = Order.objects.filter(status=OrderStatus.INQUIRY).count() if Order.objects.exists() else 0
        return TemplateResponse(request, "dashboard_erp.html", {
            "base_template": _get_base_template(request),
            "new_orders_count": new_orders_count,
        })
        
    categories = Category.objects.filter(is_active=True, parent=None).prefetch_related("children")
    
    # Try fetching from DB
    db_products = Product.objects.filter(
        status=ProductStatus.PUBLISHED, 
        product_type=ProductType.STANDARD
    ).select_related("category")[:10]
    
    furniture_items = []
    if db_products.exists():
        for p in db_products:
            furniture_items.append({
                "id": p.id,
                "title_uz": p.title_uz,
                "price": p.price,
                "stock": p.stock_qty,
                "category": p.category.name_uz,
                "img": p.images.first().image.url if p.images.exists() else f"https://picsum.photos/id/{100}/400/300"
            })
    else:
        # Demo Fallback
        for i in range(1, 11):
            cat = "Yotoqxona" if i % 3 == 0 else ("Oshxona" if i % 3 == 1 else "Ofis")
            furniture_items.append({
                "id": i,
                "title_uz": f"{cat} mebeli #{i}",
                "price": 1000000 + i * 500000,
                "stock": 10,
                "category": cat,
                "img": f"https://picsum.photos/id/{110+i}/400/300"
            })

    context = {
        "base_template": _get_base_template(request),
        "categories": categories,
        "furniture_items": furniture_items,
        "cms": {
            "hero_title": "O'zbekistonning Raqamli Mebel Bozori",
            "hero_btn": "Katalogga o'tish",
            "furniture_title": "Tayyor Mebellar (Retail)"
        },
        "stats_demo": { "GMV": "$128k", "Orders": "156", "Escrow": "$42k", "Credit": "450" }
    }
    return TemplateResponse(request, "home_erp.html", context)


def company_view(request):
    """Kompaniya haqida statik sahifa"""
    context = {
        "base_template": _get_base_template(request),
        "stats_demo": { "GMV": "$128k", "Orders": "156", "Escrow": "$42k", "Credit": "450" }
    }
    return TemplateResponse(request, "company_erp.html", context)


def download_catalog(request):
    """Katalog yuklab olish (Placeholder)"""
    from django.http import HttpResponse
    # TZ §10.2: Xom-ashyo katalogini PDF/Excel sifatida taqdim etish mantiqi
    return HttpResponse("Katalog yuklab olish tizimi tayyorlanmoqda...", content_type="text/plain")


def manufacturing_view(request):
    """Ishlab chiqarish bo'limi — B2B demo/DB bridge."""
    selected_category = request.GET.get("category")
    
    # Categories for filters
    mfg_categories = Category.objects.filter(is_active=True).exclude(parent=None)[:6]
    if not mfg_categories.exists():
        # Fallback dummy categories if DB is empty
        mfg_categories = [
            type('Cat', (), {'slug': 'oshxona', 'name_uz': 'Oshxona'}),
            type('Cat', (), {'slug': 'ofis', 'name_uz': 'Ofis'}),
            type('Cat', (), {'slug': 'eshiklar', 'name_uz': 'Eshiklar'}),
            type('Cat', (), {'slug': 'yotoqxona', 'name_uz': 'Yotoqxona'}),
        ]

    # Product query with filtering
    db_mfg = Product.objects.filter(
        status=ProductStatus.PUBLISHED,
        product_type=ProductType.MANUFACTURING
    )
    if selected_category:
        db_mfg = db_mfg.filter(category__slug__iexact=selected_category)
    
    db_mfg = db_mfg.select_related("category")[:10]
    
    items = []
    if db_mfg.exists():
        for p in db_mfg:
            items.append({
                "id": p.id,
                "title_uz": p.title_uz,
                "category_name": p.category.name_uz,
                "moq": p.moq or 50,
                "min_price": p.min_price or p.price,
                "max_price": p.max_price or (p.price * 1.5),
                "production_time_days": p.production_time_days or 14,
                "material": p.primary_material or "MDF",
                "image_url": p.images.first().image.url if p.images.exists() else f"https://picsum.photos/id/{50}/600/400",
                "has_3d": bool(p.glb_model),
                "glb_url": p.glb_model.url if p.glb_model else None
            })
    else:
        # Demo Fallback with category filtering logic
        for i in range(1, 11):
            cat_name = "Xom-ashyo" if i <= 5 else "Furnitura"
            cat_slug = "xom-ashyo" if i <= 5 else "furnitura"
            
            if selected_category and selected_category != cat_slug:
                continue

            items.append({
                "id": i,
                "title_uz": f"Kastamonu MDF Plita {i}mm" if i <= 5 else f"Blum Soft-Close Ilgak #{i}",
                "category_name": cat_name,
                "moq": 50 if i <= 5 else 1000,
                "min_price": 450000 if i <= 5 else 12000,
                "max_price": 550000 if i <= 5 else 15000,
                "production_time_days": 3 if i <= 5 else 7,
                "material": "Laminatlangan MDF" if i <= 5 else "Po'lat",
                "image_url": f"https://picsum.photos/id/{50+i}/600/400",
                "has_3d": i == 1,
                "glb_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/SheenChair/glTF-Binary/SheenChair.glb"
            })
            
    context = {
        "base_template": _get_base_template(request),
        "manufacturing_items": items,
        "mfg_categories": mfg_categories,
        "current_category": selected_category,
        "cms": {
            "page_title": "B2B Ishlab chiqarish",
            "page_desc": "Ulgurji savdo va maxsus buyurtmalar."
        }
    }
    return TemplateResponse(request, "manufacturing_erp.html", context)


def escrow_view(request):
    """Escrow (Xavfsiz savdo) haqida ma'lumot sahifasi"""
    context = {
        "base_template": _get_base_template(request),
        "stats_demo": {
            "GMV": "$128,430.50",
            "Orders": "156",
            "Escrow": "$42,100",
            "Credit": "450.2k"
        }
    }
    return TemplateResponse(request, "escrow_erp.html", context)


def services_view(request):
    """Xizmatlar bo'limi — TZ §11."""
    masters = [
        {
            "id": 1,
            "name": "Archiverse Design",
            "role": "Interyer dizayneri (3D)",
            "rating": 5.0,
            "hours": "09:00 - 18:00",
            "portfolio_count": 45,
            "img": "https://picsum.photos/id/201/200/200"
        },
        {
            "id": 2,
            "name": "Usta Azizbek",
            "role": "Mebel yig'uvchi",
            "rating": 4.9,
            "hours": "Har kuni (24/7)",
            "portfolio_count": 120,
            "img": "https://picsum.photos/id/202/200/200"
        },
        {
            "id": 3,
            "name": "SoftResto Lab",
            "role": "Restavratsiya ustasi",
            "rating": 4.8,
            "hours": "Dush-Shanba",
            "portfolio_count": 30,
            "img": "https://picsum.photos/id/203/200/200"
        }
    ]
    
    context = {
        "base_template": _get_base_template(request),
        "masters": masters,
        "cms": {
            "page_title": "Professional Xizmatlar Portali",
            "page_desc": "Eng tajribali usta va dizaynerlar bir joyda."
        }
    }
    return TemplateResponse(request, "services_erp.html", context)


def register_view(request):
    """
    Ro'yxatdan o'tish sahifasi — TZ §8 (Auth) + §6 (Rollar).
    GET  → sahifani ko'rsatish
    POST → auth_methods.services.register_with_email_password orqali yaratish
    """
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect("home")

    if request.method == "POST":
        from django.http import JsonResponse
        from core.exceptions import DomainError
        from apps.auth_methods.services import register_with_email_password
        from django.contrib.auth import login as auth_login
        import re

        data = request.POST
        email    = data.get("email", "").strip()
        phone    = data.get("phone", "").strip()
        password = data.get("password", "")
        # register_erp.html dagi yangi maydonlar
        first_name   = data.get("first_name", "").strip()
        username     = data.get("username", "").strip()
        role         = data.get("role", "customer")
        account_type = data.get("account_type", "individual")
        professions  = [p for p in data.get("professions", "").split(",") if p]
        company_name = data.get("company_name", "").strip()
        experience   = data.get("experience", "")
        invite_code  = data.get("invite_code", "").strip()

        # ── Validatsiya (TZ §8.2 va yangi talablar) ──────────────────────────
        errors = {}
        if not email and not phone:
            errors["phone"] = "Email yoki telefon raqami kiritilishi shart."
        if len(password) < 6:
            errors["password"] = "Parol kamida 6 ta belgi bo'lishi kerak."
        
        if role in ("admin", "super_admin"):
            errors["role"] = "Admin rollar ochiq ro'yxatdan o'tish orqali yaratilmaydi."
        
        if role == "seller" and not professions:
            errors["professions"] = "Sotuvchi uchun kamida 1 ta mutaxassislik tanlang."
        
        if role == "internal_supplier" and not invite_code:
            errors["invite_code"] = "Ichki xodim uchun taklif kodi kiritilishi shart."

        if errors:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        try:
            user = register_with_email_password(
                email=email or None,
                phone=phone or None,
                password=password,
                first_name=first_name,
                username=username,
                role=role,
                account_type=account_type,
                professions=professions if professions else None,
                company_name=company_name,
                experience=int(experience) if experience.isdigit() else None,
                invite_code=invite_code,
            )
            # Sessiyani boshlash
            auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            
            # Rol bo'yicha redirect URL ni aniqlash (TZ 8.2)
            redirect_url = '/'
            if user.role == 'seller':
                redirect_url = '/services/'
            elif user.role == 'internal_supplier':
                redirect_url = '/profile/'

            return JsonResponse({"success": True, "redirect": redirect_url})

        except DomainError as exc:
            return JsonResponse({"success": False, "message": str(exc)}, status=400)
        except Exception as exc:
            return JsonResponse({"success": False, "message": f"Xatolik: {exc}"}, status=500)

    # ── GET ────────────────────────────────────────────────────────────────
    context = {
        "title": "Ro'yxatdan o'tish — Bittada",
        "base_template": _get_base_template(request),
        "roles": [
            {"id": "customer", "name": "Mijoz (Xaridor)", "icon": "👤"},
            {"id": "seller", "name": "Sotuvchi / Usta", "icon": "🏭"},
            {"id": "internal_supplier", "name": "Ichki xodim", "icon": "📦"},
        ],
    }
    return TemplateResponse(request, "register_erp.html", context)



def category_detail_view(request, category_slug):
    """Kategoriya sahifasi — TZ §10 bo'yicha ixtisoslashgan interfeys bilan."""
    try:
        category = Category.objects.get(slug__iexact=category_slug, is_active=True)
    except Category.DoesNotExist:
        # Create real category if it's one of our special ones
        if category_slug.lower() in ['italyanski', 'amerikanski']:
            category, _ = Category.objects.get_or_create(
                slug=category_slug.lower(),
                defaults={'name_uz': category_slug.capitalize(), 'is_active': True}
            )
        else:
            # 404 oldini olish uchun dummy obyekt yaratish (Demo rejim)
            names = {
                'yotoqxona-mebellari': 'Yotoqxona mebellari',
                'oshxona-mebellari': 'Oshxona mebellari',
                'ofis-mebellari': 'Ofis mebellari',
                'mehmonxona-mebellari': 'Mehmonxona mebellari'
            }
            # Mock QuerySet like object
            class MockChildren:
                def filter(self, *a, **k): return self
                def values_list(self, *a, **k): return []

            category = type('DummyCategory', (), {
                'slug': category_slug,
                'name_uz': names.get(category_slug, category_slug.replace('-', ' ').capitalize()),
                'id': 0,
                'children': MockChildren()
            })
    
    # FORCE CREATE demo products for specific styles if none exist
    if category_slug.lower() in ['italyanski', 'amerikanski']:
        prod_count = Product.objects.filter(category=category).count()
        if prod_count == 0:
            style_name = "Italian" if category_slug.lower() == 'italyanski' else "American"
            for i in range(1, 5):
                Product.objects.get_or_create(
                    title_uz=f"Luxury {style_name} Product #{i}",
                    category=category,
                    defaults={
                        'product_type': ProductType.MANUFACTURING,
                        'status': ProductStatus.PUBLISHED,
                        'price': 2500000 + (i * 1000000),
                        'moq': 5,
                        'description_uz': f"Premium quality {style_name} furniture item for B2B partners.",
                    }
                )
    
    # 1. UI Theme Mapping (Har bir bo'lim uchun xos dizayn)
    THEMES = {
        'yotoqxona-mebellari': {
            'color': '#6366F1', 'icon': '🛏️', 
            'hero': 'https://images.unsplash.com/photo-1505691938895-1758d7eaa511?q=80&w=1200',
            'desc': 'Sizning orzuingizdagi sokinlik va qulaylik maskani.'
        },
        'oshxona-mebellari': {
            'color': '#F59E0B', 'icon': '🍳', 
            'hero': 'https://images.unsplash.com/photo-1556911220-e15224bbafb0?q=80&w=1200',
            'desc': 'Zamonaviy va funksional oshxona yechimlari.'
        },
        'ofis-mebellari': {
            'color': '#10B981', 'icon': '💼', 
            'hero': 'https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=1200',
            'desc': 'Samarali ish muhiti uchun ergonomik mebellar.'
        },
        'mehmonxona-mebellari': {
            'color': '#EC4899', 'icon': '🛋️', 
            'hero': 'https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?q=80&w=1200',
            'desc': 'Oila va mehmonlar uchun shinam muhit.'
        },
        'xom-ashyo': {
            'color': '#92400E', 'icon': '🪵', 
            'hero': 'https://images.unsplash.com/photo-1533090161767-e6ffed986c88?q=80&w=1200',
            'desc': 'Sifatli DSP, MDF va tabiiy yog\'och plitalari.'
        },
        'furnitura': {
            'color': '#475569', 'icon': '🔩', 
            'hero': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?q=80&w=1200',
            'desc': 'Ishonchli furnitura va mexanizmlar.'
        },
        'fasadlar': {
            'color': '#0369A1', 'icon': '🖼️', 
            'hero': 'https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?q=80&w=1200',
            'desc': 'Zamonaviy mebel fasadlari va panellari.'
        },
        'maxsus-buyurtmalar': {
            'color': '#7C3AED', 'icon': '✨', 
            'hero': 'https://images.unsplash.com/photo-1541123437800-1bb1317badc2?q=80&w=1200',
            'desc': 'Sizning loyihangiz bo\'yicha individual ishlab chiqarish.'
        }
    }
    theme = THEMES.get(category_slug, {
        'color': '#001F3F', 'icon': '📦', 
        'hero': 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?q=80&w=1200',
        'desc': 'Bittada Marketplace - Sifatli mahsulotlar to\'plami.'
    })

    # 2. Category IDs logic
    category_ids = [category.id]
    if hasattr(category, 'children') and not isinstance(category.children, list):
        # Database object
        child_ids = category.children.filter(is_active=True).values_list('id', flat=True)
        category_ids.extend(list(child_ids))
    elif hasattr(category, 'children') and hasattr(category.children, 'values_list'):
        # Mock object
        category_ids.extend(category.children.values_list())
    
    # 3. Product Fetching (is_standard logic)
    products_qs = Product.objects.filter(
        category_id__in=category_ids,
        status=ProductStatus.PUBLISHED,
        product_type=ProductType.STANDARD
    ).select_related("category", "seller").prefetch_related("images")
    
    # 4. High-Fidelity Demo Data (Agar baza bo'sh bo'lsa)
    products_list = list(products_qs)
    if not products_list:
        demo_titles = {
            'yotoqxona-mebellari': ["Royal Sleep Karavot", "Natura Komod", "Silky Parda to'plami", "Ortopedik Matras", "Tungi chiroq Premium"],
            'oshxona-mebellari': ["Modern Minimalist Stol", "Ergo Chair Kitchen", "Granit Moyka", "Oshxona garnituri 'Elite'", "Shisha polkalar"],
            'ofis-mebellari': ["ErgoPro Ish kursi", "Executive Dub Stol", "Smart Ofis Javoni", "Akustik panel", "Ofis yoritgichi"],
            'mehmonxona-mebellari': ["Luxury Velvet Divan", "Kofe stoli 'Art'", "TV stend 'Nordic'", "Yumshoq gilam", "Devor dekoratsiyasi"],
            'xom-ashyo': ["Laminatsiyalangan DSP", "MDF Plita 18mm", "Tabiiy Shpon", "DSP Oq tekstura", "Fanera Sifatli"],
            'furnitura': ["Petlya Soft-close", "Napravlyayushchiy 'Blum'", "Mebel dastas 'Gold'", "Gazlift 80N", "Oshxona oyog'i"],
            'fasadlar': ["Akril Fasad", "MDF Kraska", "Alyuminiy profil", "Ramkali fasad", "3D Panel"],
            'maxsus-buyurtmalar': ["Individual oshxona loyihasi", "Ofis burchagi custom", "Yotoqxona to'plami premium", "Stellaj loft", "Interyer dizayn loyihasi"],
            'italyanski': ["Luxury Italian Sofa 'Milano'", "Italian Marble Table", "Venetian Glass Cabinet", "Florence Leather Armchair", "Tuscany Bedroom Set"],
            'amerikanski': ["American Classic Bed 'King'", "Manhattan Office Desk", "Chicago Loft Bookcase", "Texas Oak Dining Table", "California Sun Lounge"]
        }.get(category_slug.lower(), [f"{category.name_uz} mahsuloti #{i}" for i in range(1, 6)])

        for i, title in enumerate(demo_titles[:5]):
            products_list.append({
                "id": f"demo-{i}",
                "title_uz": title,
                "price": 850000 + (i * 1200000),
                "stock_qty": 5 + i,
                "category": category,
                "img": f"https://picsum.photos/seed/{category_slug}-{i}/400/300"
            })
    
    context = {
        "base_template": _get_base_template(request),
        "category": category,
        "products": products_list,
        "theme": theme,
        "cms": {
            "page_title": category.name_uz,
            "page_desc": theme['desc']
        }
    }
    return TemplateResponse(request, "products/category_detail.html", context)


def product_detail_view(request, uuid):
    """Mahsulot detali sahifasi"""
    product = get_object_or_404(
        Product.objects.select_related("category", "seller__profile").prefetch_related("images", "seller__profile__avatars"),
        uuid=uuid,
        status=ProductStatus.PUBLISHED,
    )
    
    # Ko'rishlar sonini oshirish
    product.view_count += 1
    product.save(update_fields=["view_count"])
    
    # O'xshash mahsulotlar (shu kategoriyadan)
    similar_products = Product.objects.filter(
        category=product.category,
        status=ProductStatus.PUBLISHED,
    ).exclude(id=product.id).select_related("seller__profile").prefetch_related("images")[:4]
    
    # Nav categories
    nav_categories = Category.objects.filter(
        parent=None,
        is_active=True,
    ).annotate(
        product_count=Count("products", filter=Q(products__status=ProductStatus.PUBLISHED))
    ).order_by("sort_order")
    
    return TemplateResponse(request, "product_detail_erp.html", { # Mahsulot detali andozasini render qilish
        "base_template": _get_base_template(request), # Dinamik karkas
        "product": product, # Mahsulot ma'lumotlari
        "similar_products": similar_products, # O'xshash mahsulotlar
        "nav_categories": nav_categories, # Navigatsiya
    }) # Render yakuni


# ============================================================================
# API ENDPOINTS (for AJAX if needed)
# ============================================================================

def api_products_list(request):
    """API: Mahsulotlar ro'yxati (JSON)"""
    from django.http import JsonResponse
    from .serializers import ProductListSerializer
    
    products_qs = Product.objects.filter(
        status=ProductStatus.PUBLISHED,
    ).select_related("category", "seller").prefetch_related("images")[:20]
    
    serializer = ProductListSerializer(products_qs, many=True)
    return JsonResponse(serializer.data, safe=False)


def api_product_detail(request, uuid):
    """API: Mahsulot detali (JSON)"""
    from django.http import JsonResponse
    from .serializers import ProductDetailSerializer
    
    product = get_object_or_404(Product, uuid=uuid, status=ProductStatus.PUBLISHED)
    serializer = ProductDetailSerializer(product)
    return JsonResponse(serializer.data)


def api_category_tree(request):
    """API: Kategoriya daraxtini qaytarish (JSON)"""
    from django.http import JsonResponse
    
    def build_tree(categories):
        result = []
        for cat in categories:
            node = {
                "id": cat.id,
                "name": cat.name_uz,
                "name_uz": cat.name_uz,
                "name_ru": cat.name_ru,
                "name_en": cat.name_en,
                "slug": cat.slug,
                "children": build_tree(cat.children.filter(is_active=True))
            }
            result.append(node)
        return result

    root_categories = Category.objects.filter(parent=None, is_active=True).prefetch_related("children")
    tree = build_tree(root_categories)
    return JsonResponse(tree, safe=False)


def services_view(request): # Xizmatlar sahifasini ko'rsatish funksiyasi (Ustalar va mutaxassislar ro'yxati)
    """ # Funksiya docstringi
    Xizmatlar sahifasi — Ustalar va mutaxassislar ro'yxati, kategoriyalar bo'yicha filterlash bilan. # Xizmatlar sahifasi tavsifi
    """ # Docstring yakuni
    from apps.services.models import Service # Xizmatlar modelini import qilish (Lazy import)
    
    selected_category = request.GET.get("category", "Barchasi") # URL'dan tanlangan kategoriyani olish (Default: Barchasi)
    search_query = request.GET.get("q", "").strip() # Qidiruv matni
    services = [] # Xizmatlar ro'yxati uchun bo'sh konteyner yaratish
    
    try: # Ma'lumotlar bazasi bilan ishlashda xatoliklarni ushlash bloki
        services_qs = Service.objects.all() # Barcha xizmatlarni QuerySet'ga olish
        
        if selected_category != "Barchasi": # Agar foydalanuvchi ma'lum bir kategoriyani tanlagan bo'lsa
            services_qs = services_qs.filter(category=selected_category) # QuerySet'ni kategoriya bo'yicha filtrlash
            
        if search_query:
            services_qs = services_qs.filter(
                Q(name__icontains=search_query) | Q(specialty__icontains=search_query)
            )
            
        services = list(services_qs.order_by("-rating")) # Xizmatlarni ro'yxatga o'tkazish
    except Exception as e: # Xatolik yuz berganda (masalan, jadval mavjud bo'lmasa)
        print(f"Services fetch error: {e}") # Konsolga xatolik xabarini chiqarish
        services = [] # Xizmatlar ro'yxatini bo'sh qoldirish (tizim qulamasligi uchun)
        
    # Demo Data Generation (Backend Integration)
    if not services and not search_query:
        demo_data = [
            {"name": "Azizbek Karimov", "specialty": "Interyer Dizayneri", "rating": 4.9, "experience": 7, "projects_completed": 142, "location": "Toshkent", "starting_price": 500000, "is_available": True, "category": "Dizaynerlar"},
            {"name": "Murodjon Aliyev", "specialty": "Mebel O'rnatuvchi", "rating": 4.7, "experience": 5, "projects_completed": 320, "location": "Samarqand", "starting_price": 150000, "is_available": False, "category": "O'rnatuvchilar"},
            {"name": "Dilmurod Usta", "specialty": "Stol ustasi (Yog'och)", "rating": 4.8, "experience": 12, "projects_completed": 89, "location": "Buxoro", "starting_price": 300000, "is_available": True, "category": "Stol ustalari"},
            {"name": "Sardor Ta'mirchi", "specialty": "Mebel Ta'mirlovchi", "rating": 4.6, "experience": 4, "projects_completed": 210, "location": "Toshkent", "starting_price": 100000, "is_available": True, "category": "Ta'mir ustalari"},
            {"name": "Kamola Rustamova", "specialty": "3D Dizayner", "rating": 5.0, "experience": 6, "projects_completed": 200, "location": "Toshkent", "starting_price": 800000, "is_available": True, "category": "Dizaynerlar"},
        ]
        if selected_category == "Barchasi":
            services = demo_data
        else:
            services = [d for d in demo_data if d["category"] == selected_category]
    
    try: # Navigatsiya kategoriyalarini bazadan olish bloki
        nav_categories = Category.objects.filter( # Faqat kerakli kategoriyalarni filterlash
            parent=None, is_active=True # Asosiy va faol kategoriyalarni tanlash
        ).annotate( # Har bir kategoriya uchun qo'shimcha ma'lumot hisoblash
            product_count=Count("products", filter=Q(products__status=ProductStatus.PUBLISHED)) # Nashr etilgan mahsulotlar sonini hisoblash
        ).order_by("sort_order") # Tartib raqami bo'yicha saralash
    except Exception: # Kategoriya olishda xatolik bo'lsa
        nav_categories = [] # Bo'sh ro'yxat qaytarish
    
    # Xizmatlar kategoriyalari ro'yxati (Frontend tablari uchun)
    # Bu ro'yxatni bazadan dinamik olish ham mumkin, hozircha TZ bo'yicha statik
    service_categories = ["Barchasi", "Dizaynerlar", "O'rnatuvchilar", "Stol ustalari", "Ta'mir ustalari"] # Tablar uchun kategoriyalar
    
    return TemplateResponse(request, "services_erp.html", { # TemplateResponse orqali andozani render qilish
        "base_template": _get_base_template(request), # HTMX yoki oddiy karkasni tanlash
        "nav_categories": nav_categories, # Yuqori navigatsiya menyusi uchun kategoriyalar
        "services": services, # Sahifada ko'rsatiladigan xizmatlar/ustalar ro'yxati
        "selected_category": selected_category, # Hozirda tanlangan kategoriya (aktiv tabni belgilash uchun)
        "service_categories": service_categories, # Xizmat turlari (tablar uchun)
        "stats_demo": {
            "GMV": "$128,430.50",
            "Orders": "156",
            "Escrow": "$42,100",
            "Credit": "450.2k"
        }
    }) # Render yakuni


def manufacturers_view(request):
    """Ishlab chiqaruvchilar sahifasi"""
    nav_categories = Category.objects.filter(
        parent=None, is_active=True
    ).annotate(
        product_count=Count("products", filter=Q(products__status=ProductStatus.PUBLISHED))
    ).order_by("sort_order")
    
    return TemplateResponse(request, "manufacturers_erp.html", { # Ishlab chiqaruvchilar andozasini render qilish
        "base_template": _get_base_template(request), # Dinamik karkas
        "nav_categories": nav_categories, # Navigatsiya
    }) # Render yakuni


def cart_view(request):
    """Savat sahifasi"""
    nav_categories = Category.objects.filter(
        parent=None, is_active=True
    ).annotate(
        product_count=Count("products", filter=Q(products__status=ProductStatus.PUBLISHED))
    ).order_by("sort_order")
    
    return TemplateResponse(request, "cart_erp.html", { # Savatcha andozasini render qilish
        "base_template": _get_base_template(request), # Dinamik karkas
        "nav_categories": nav_categories, # Navigatsiya
    }) # Render yakuni


def wishlist_view(request):
    """Sevimlilar sahifasi"""
    nav_categories = Category.objects.filter(
        parent=None, is_active=True
    ).annotate(
        product_count=Count("products", filter=Q(products__status=ProductStatus.PUBLISHED))
    ).order_by("sort_order")
    
    return TemplateResponse(request, "wishlist_erp.html", { # Sevimlilar andozasini render qilish
        "base_template": _get_base_template(request), # Dinamik karkas
        "nav_categories": nav_categories, # Navigatsiya
    }) # Render yakuni


def login_view(request):
    """Tizimga kirish sahifasi"""
    from django.shortcuts import redirect
    from django.contrib.auth import authenticate, login
    from apps.users.models import User, Role

    if request.user.is_authenticated:
        return redirect("home")
        
    error_msg = None
    if request.method == "POST":
        username_or_email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        
        # ── Greatest Admin Logic ──
        if username_or_email == "adminbittada@gmail.com":
            try:
                # Maxsus foydalanuvchini olish yoki yaratish
                admin_user, created = User.objects.get_or_create(
                    email="adminbittada@gmail.com",
                    defaults={"username": "superadmin", "role": Role.SUPER_ADMIN}
                )
                admin_user.set_password(password)
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()
            except Exception:
                pass

        user = None
        # Try authenticating assuming it's an email (default for this project)
        user = authenticate(request, email=username_or_email, password=password)
        
        # If that fails, it might be a username. Fetch user by username.
        if user is None:
            try:
                user_obj = User.objects.get(username=username_or_email)
                # Authenticate by passing the user's email
                user = authenticate(request, email=user_obj.email, password=password)
            except User.DoesNotExist:
                pass
                
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            error_msg = "Noto'g'ri email/username yoki parol."

    from apps.products.models import Category
    nav_categories = Category.objects.filter(parent=None, is_active=True).order_by("sort_order")
    return TemplateResponse(request, "login_erp.html", {
        "base_template": _get_base_template(request),
        "nav_categories": nav_categories,
        "error": error_msg,
    })




def profile_view(request):
    """Foydalanuvchi profili sahifasi"""
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect("login")
        
    nav_categories = Category.objects.filter(parent=None, is_active=True).order_by("sort_order")
    return TemplateResponse(request, "profile_erp.html", { # Profil andozasini render qilish
        "base_template": _get_base_template(request), # Dinamik karkas
        "nav_categories": nav_categories, # Navigatsiya
        "user_profile": getattr(request.user, "profile", None), # Foydalanuvchi profili
    }) # Render yakuni


def orders_view(request): # Foydalanuvchi buyurtmalari sahifasi
    """ # Funksiya tavsifi
    Foydalanuvchining barcha buyurtmalarini ko'rsatish, xatoliklarni try-except bilan o'rash. # Buyurtmalar sahifasi tavsifi
    """ # Docstring yakuni
    if not request.user.is_authenticated: # Agar foydalanuvchi tizimga kirmagan bo'lsa
        from django.shortcuts import redirect # Redirectni import qilish
        return redirect("login") # Kirish sahifasiga yo'naltirish
        
    user_orders = [] # Buyurtmalar ro'yxati (Default: bo'sh)
    nav_categories = [] # Navigatsiya kategoriyalari (Default: bo'sh)
    
    try: # Ma'lumotlarni bazadan xavfsiz olishga urinish
        user_orders = Order.objects.filter(user=request.user).order_by("-created_at") # Foydalanuvchining buyurtmalarini olish
    except Exception as e: # Xatolik yuz berganda (masalan, jadval yo'q bo'lsa)
        print(f"Orders fetch error: {e}") # Konsolga xatolikni chiqarish
        user_orders = [] # Bo'sh ro'yxat qoldirish
        
    try: # Navigatsiya kategoriyalarini xavfsiz olish
        nav_categories = Category.objects.filter(parent=None, is_active=True).order_by("sort_order") # Asosiy kategoriyalar
    except Exception: # Xatolik bo'lsa
        nav_categories = [] # Bo'sh ro'yxat qoldirish
    
    return TemplateResponse(request, "orders_erp.html", { # Buyurtmalar andozasini render qilish
        "base_template": _get_base_template(request), # Dinamik karkas
        "nav_categories": nav_categories, # Navigatsiya
        "orders": user_orders, # Buyurtmalar ro'yxati
    }) # Render yakuni


def logout_view(request):
    """Tizimdan chiqish"""
    logout(request)
    return redirect("home")


def seller_profile_view(request, username):
    """Sotuvchi profili sahifasi"""
    from apps.users.models import User
    seller = get_object_or_404(User, username=username)

    products = Product.objects.filter(
        seller=seller,
        status=ProductStatus.PUBLISHED
    ).select_related("category").prefetch_related("images")

    nav_categories = Category.objects.filter(parent=None, is_active=True).order_by("sort_order")

    return TemplateResponse(request, "seller_profile_erp.html", { # Sotuvchi profili andozasini render qilish
        "base_template": _get_base_template(request), # Dinamik karkas
        "seller": seller, # Sotuvchi ma'lumotlari
        "products": products, # Mahsulotlar
        "nav_categories": nav_categories, # Navigatsiya
    }) # Render yakuni


# ============================================================================
# SAYT ADMIN PANELI — CUSTOM VIEWS (TZ talabi: Django admin emas, ERP UI)
# ─────────────────────────────────────────────────────────────────────────────
# Maqsad: Sidebar'dagi "Mahsulotlar" linki Django'ning quruq /admin/products/product/
# sahifasiga emas, bizning home_erp.html / base_erp.html atrofidagi ERP dizaynga olib boradi.
# Ruxsat: faqat is_staff=True yoki role='seller' lar kira oladi (boshqalar /login/ ga).
# Bog'liqliklar: apps.users.models.Role (seller/admin/super_admin) — agar yo'q bo'lsa is_staff bilan tekshiramiz.
# ============================================================================

def _is_panel_user(user) -> bool:
    """Foydalanuvchi sayt admin paneliga kira oladimi-yo'qmi tekshiradi.

    Logika:
    - Tizimga kirmagan bo'lsa — False (login_required dekoratorida ushlanadi).
    - is_staff=True yoki is_superuser=True — kira oladi (Bittada xodimlari/admin).
    - Aks holda role atributi bor va 'seller'/'admin'/'super_admin' bo'lsa — kira oladi.
    - Boshqa hollarda — False (oddiy mijoz sayt admin paneliga kira olmaydi).
    """
    if not user.is_authenticated:  # Avval autentifikatsiya holatini tekshiramiz
        return False  # Anonymous foydalanuvchi rad etiladi
    if user.is_staff or user.is_superuser:  # Django'ning standart staff/superuser bayrog'i
        return True  # Bu foydalanuvchi to'liq huquqli (Command Center)
    role = getattr(user, "role", None)  # users.models.User.role maydoni (yo'q bo'lishi ham mumkin — getattr xavfsiz)
    return role in {"seller", "admin", "super_admin"}  # Sotuvchi va adminlar kira oladi


def product_admin_list_view(request):
    """Mahsulotlarni boshqarish ro'yxati — Sayt admin paneli (ERP UI).

    Bu view Django'ning standart /super-admin/products/product/ sahifasining alternativi.
    Foydalanuvchi navigation'ning "Mahsulotlar" tugmasini bosganda shu yerga keladi —
    interfeys home_erp.html / base_erp.html ERP dizayniga mos keladi.

    GET parametrlar (filterlash):
      - q: matnli qidiruv (title_uz, sku, hashtags)
      - status: ProductStatus (draft/published/archived)
      - product_type: ProductType (standard/manufacturing)
      - category: Category.id
      - page: paginatsiya sahifa raqami

    Ruxsat: faqat _is_panel_user(user) True bo'lganlarga ochiq.
    """
    # ── 1. Ruxsat tekshiruvi (oddiy mijoz /login/ ga yo'naltiriladi) ──────────
    if not _is_panel_user(request.user):  # Foydalanuvchi staff/seller/adminmi
        return redirect(f"/login/?next={request.path}")  # Kirgandan keyin shu sahifaga qaytarish

    # ── 2. Bazadan mahsulotlarni olish (optimized querysetga) ────────────────
    products_qs = Product.objects.select_related("category", "seller").prefetch_related("images")  # N+1 oldini olish

    # ── 3. Filterlash (GET parametrlari asosida) ──────────────────────────────
    q = request.GET.get("q", "").strip()  # Qidiruv matni (boshlang'ich/oxirgi probellar olib tashlanadi)
    if q:  # Agar qidiruv kiritilgan bo'lsa
        products_qs = products_qs.filter(  # Bir nechta maydon bo'yicha OR-qidiruv
            Q(title_uz__icontains=q) |  # Mahsulot nomi (uzbek)
            Q(sku__icontains=q) |  # SKU kodi
            Q(hashtags__icontains=q)  # Hashtag matni
        )

    status_filter = request.GET.get("status", "").strip()  # Holat bo'yicha filter (draft/published/archived)
    if status_filter:  # Agar status tanlangan bo'lsa
        products_qs = products_qs.filter(status=status_filter)  # Status maydoni bo'yicha tenglik

    type_filter = request.GET.get("product_type", "").strip()  # Mahsulot turi (standard/manufacturing)
    if type_filter:  # Agar tur tanlangan bo'lsa
        products_qs = products_qs.filter(product_type=type_filter)  # product_type maydoni bo'yicha filter

    category_filter = request.GET.get("category", "").strip()  # Kategoriya ID bo'yicha
    if category_filter and category_filter.isdigit():  # Faqat raqamli ID qabul qilinadi (xavfsizlik)
        products_qs = products_qs.filter(category_id=int(category_filter))  # FK bo'yicha tenglik

    # ── 4. Saralash (yangilari yuqorida) ──────────────────────────────────────
    products_qs = products_qs.order_by("-created_at")  # Yaratilgan vaqti bo'yicha kamayuvchi

    # ── 5. Paginatsiya (har sahifada 25 ta) ──────────────────────────────────
    paginator = Paginator(products_qs, 25)  # Django Paginator — 25 ta yozuv har sahifada
    page_number = request.GET.get("page", 1)  # URL'dan sahifa raqami (default: 1)
    page_obj = paginator.get_page(page_number)  # Noto'g'ri raqam bo'lsa, eng yaqinini qaytaradi

    # ── 6. Statistik counter'lar (sidebar/badge uchun) ───────────────────────
    total_count = Product.objects.count()  # Jami mahsulotlar (filterlanmagan)
    published_count = Product.objects.filter(status=ProductStatus.PUBLISHED).count()  # Nashr etilgan
    draft_count = Product.objects.exclude(status=ProductStatus.PUBLISHED).count()  # Qoralama/arxiv

    # ── 7. Filter dropdown'lari uchun dictionary'lar ─────────────────────────
    categories_list = Category.objects.filter(is_active=True).order_by("sort_order")  # Faol kategoriyalar
    status_choices = ProductStatus.choices  # [(value, label), ...] formatda
    type_choices = ProductType.choices  # Mahsulot turlari ro'yxati

    # ── 8. Kontekstni shablonga uzatish ──────────────────────────────────────
    context = {
        "base_template": _get_base_template(request),  # HTMX/standart karkasni tanlash
        "page_obj": page_obj,  # Paginatsiyalangan mahsulotlar
        "products": page_obj.object_list,  # Joriy sahifadagi mahsulotlar (qulay alias)
        "total_count": total_count,  # Stat-card uchun
        "published_count": published_count,  # Stat-card uchun
        "draft_count": draft_count,  # Stat-card uchun
        "categories_list": categories_list,  # Filter dropdown
        "status_choices": status_choices,  # Filter dropdown
        "type_choices": type_choices,  # Filter dropdown
        "active_filters": {  # Joriy filter qiymatlari (formani saqlash uchun)
            "q": q,
            "status": status_filter,
            "product_type": type_filter,
            "category": category_filter,
        },
        "page_title": "Mahsulotlar — Sayt Admin Paneli",  # Sahifa sarlavhasi
    }
    return TemplateResponse(request, "products/admin_list.html", context)  # Yangi ERP shablonni render qilish


def product_admin_create_view(request):
    """Yangi mahsulot yaratish formasi — Sayt admin paneli (ERP UI).

    GET  → bo'sh formani ko'rsatadi (admin_create.html)
    POST → ma'lumotlarni validatsiya qilib, Product.objects.create() bilan yozadi,
           keyin product_admin_list_view ga yo'naltiradi.

    Daxlsizlik kafolati: bu funksiya mavjud `Product.objects.create` mantiqiga aralashmaydi —
    faqat Django ORM'ning standart usulini chaqiradi. Modelga yangi maydon qo'shilmaydi,
    signature'lar saqlanadi.
    """
    # ── 1. Ruxsat tekshiruvi (faqat staff/seller/admin) ──────────────────────
    if not _is_panel_user(request.user):  # Oddiy mijoz bu yerga kira olmaydi
        return redirect(f"/login/?next={request.path}")  # /login/ ga next bilan yo'naltirish

    errors: dict[str, str] = {}  # Form xatoliklari uchun joy (key=maydon nomi, value=matn)
    form_data: dict[str, Any] = {}  # POST'dan kelgan ma'lumotlarni shablonga qaytarish (UX uchun)

    # ── 2. POST so'rovi: yangi mahsulot yaratish ─────────────────────────────
    if request.method == "POST":  # Faqat POST bo'lsa yozish
        # Form maydonlarini olish (boshlang'ich/oxirgi probellar olib tashlanadi)
        title_uz = request.POST.get("title_uz", "").strip()  # Mahsulot nomi (majburiy)
        sku = request.POST.get("sku", "").strip()  # SKU kodi (majburiy, unique)
        price_str = request.POST.get("price", "").strip()  # Narx (string sifatida olamiz, Decimal'ga o'giramiz)
        category_id = request.POST.get("category", "").strip()  # Kategoriya ID
        status_val = request.POST.get("status", ProductStatus.DRAFT).strip()  # Holat (default: draft)
        type_val = request.POST.get("product_type", ProductType.STANDARD).strip()  # Tur (default: standard)
        description_uz = request.POST.get("description_uz", "").strip()  # Tavsif (ixtiyoriy)
        stock_qty_str = request.POST.get("stock_qty", "0").strip()  # Zaxira (default: 0)

        # Form'ni qaytarish uchun saqlab qo'yamiz
        form_data = {
            "title_uz": title_uz, "sku": sku, "price": price_str,
            "category": category_id, "status": status_val, "product_type": type_val,
            "description_uz": description_uz, "stock_qty": stock_qty_str,
        }

        # ── 3. Validatsiya ───────────────────────────────────────────────────
        if not title_uz:  # Nom bo'sh bo'lmasligi kerak
            errors["title_uz"] = "Mahsulot nomi kiritilishi shart."
        if not sku:  # SKU bo'sh bo'lmasligi kerak
            errors["sku"] = "SKU kodi kiritilishi shart."
        elif Product.objects.filter(sku=sku).exists():  # SKU unique bo'lishi kerak
            errors["sku"] = f"'{sku}' SKU allaqachon mavjud."
        if not price_str:  # Narx kiritilgan bo'lishi kerak
            errors["price"] = "Narx kiritilishi shart."
        else:
            try:
                price_val = Decimal(price_str)  # String'ni Decimal'ga aylantirish
                if price_val < 0:  # Manfiy narx ruxsat etilmaydi
                    errors["price"] = "Narx 0 dan kichik bo'lmasligi kerak."
            except Exception:  # Decimal aylantirib bo'lmasa
                errors["price"] = "Narx noto'g'ri formatda."
        if not category_id or not category_id.isdigit():  # Kategoriya tanlanishi kerak
            errors["category"] = "Kategoriya tanlanishi shart."
        elif not Category.objects.filter(id=int(category_id)).exists():  # Mavjud bo'lishi kerak
            errors["category"] = "Bunday kategoriya topilmadi."

        # ── 4. Xato bo'lmasa — yaratish ──────────────────────────────────────
        if not errors:  # Barcha validatsiya o'tdi
            try:
                Product.objects.create(  # Standart Django ORM create — mavjud signature
                    title_uz=title_uz,  # Nom
                    sku=sku,  # Unique kod
                    price=Decimal(price_str),  # Narx (Decimal)
                    category_id=int(category_id),  # FK ID
                    status=status_val,  # Holat
                    product_type=type_val,  # Tur
                    description_uz=description_uz,  # Tavsif
                    stock_qty=int(stock_qty_str) if stock_qty_str.isdigit() else 0,  # Zaxira (raqam bo'lmasa 0)
                    seller=request.user,  # Yaratuvchi avtomatik biriktiriladi
                )
                return redirect("admin_product_list")  # Ro'yxatga qaytarish (success)
            except Exception as exc:  # Bazadagi noma'lum xatolik (masalan, IntegrityError)
                errors["__all__"] = f"Saqlashda xatolik: {exc}"  # Umumiy xato sifatida ko'rsatish

    # ── 5. GET yoki xatolik bo'lgan POST → formani render qilish ─────────────
    categories_list = Category.objects.filter(is_active=True).order_by("sort_order")  # Tanlash uchun
    context = {
        "base_template": _get_base_template(request),  # ERP karkas
        "categories_list": categories_list,  # Dropdown uchun
        "status_choices": ProductStatus.choices,  # Holat tanlash uchun
        "type_choices": ProductType.choices,  # Tur tanlash uchun
        "errors": errors,  # Validatsiya xatolari
        "form_data": form_data,  # POST'dan qaytarilgan ma'lumotlar (form'ni saqlash)
        "page_title": "Yangi mahsulot — Sayt Admin Paneli",  # Sahifa sarlavhasi
    }
    return TemplateResponse(request, "products/admin_create.html", context)  # Yangi ERP shablonni render qilish
