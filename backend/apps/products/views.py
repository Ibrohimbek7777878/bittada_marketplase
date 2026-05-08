"""
Products views — mebel marketplace (Django Templates).
Professionalized with Service/Selector pattern.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views import View

from .models import Category, Product, ProductStatus, ProductType
from .selectors import (
    get_root_categories_selector, 
    get_standard_products_selector, 
    get_manufacturing_products_selector,
    get_product_detail_selector,
    get_similar_products_selector,
    get_active_products_selector
)
from .services import increment_product_view_count_service

def _get_base_template(request):
    if request.headers.get("HX-Request"):
        return "base_htmx.html"
    return "base_erp.html"

# --- Main Page Views ---

def home_view(request):
    """Bosh sahifa — B2C/Retail mahsulotlar va Command Center."""
    if request.user.is_authenticated and request.user.is_superuser:
        from apps.orders.models import Order, OrderStatus
        new_orders_count = Order.objects.filter(status=OrderStatus.INQUIRY).count()
        return TemplateResponse(request, "dashboard_erp.html", {
            "base_template": _get_base_template(request),
            "new_orders_count": new_orders_count,
        })
        
    categories = get_root_categories_selector()
    furniture_items = get_standard_products_selector(limit=10)

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

def products_list_view(request):
    """Barcha mahsulotlar ro'yxati."""
    nav_categories = get_root_categories_selector()
    products_qs = get_active_products_selector()
    
    category_slug = request.GET.get("category")
    if category_slug:
        products_qs = products_qs.filter(category__slug=category_slug)

    search_q = request.GET.get("q", "").strip()
    if search_q:
        products_qs = products_qs.filter(
            Q(title_uz__icontains=search_q) | 
            Q(description_uz__icontains=search_q) |
            Q(description_ru__icontains=search_q)
        )

    return TemplateResponse(request, "shop_erp.html", {
        "base_template": _get_base_template(request),
        "nav_categories": nav_categories,
        "products": products_qs[:60],
        "search_query": search_q,
        "active_category": category_slug or "",
    })

def category_detail_view(request, category_slug):
    """Kategoriya sahifasi."""
    category = get_object_or_404(Category, slug__iexact=category_slug, is_active=True)
    category_ids = [category.id] + list(category.children.filter(is_active=True).values_list('id', flat=True))
    products_qs = get_active_products_selector().filter(category_id__in=category_ids)
    
    # Theme mapping (denormalized logic for UI)
    themes = {
        'mebel': {'icon': '🛋️', 'color': '#A4D46C', 'hero': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=1600&q=80', 'desc': "Sizning qulayligingiz bizning ustuvor vazifamiz."},
        'oshxona': {'icon': '🍽️', 'color': '#F59E0B', 'hero': 'https://images.unsplash.com/photo-1556911220-e150213ff337?auto=format&fit=crop&w=1600&q=80', 'desc': "Mazali taomlar shinam oshxonada tayyorlanadi."},
        'yotoqxona': {'icon': '🛏️', 'color': '#6366F1', 'hero': 'https://images.unsplash.com/photo-1505691938895-1758d7eaa511?auto=format&fit=crop&w=1600&q=80', 'desc': "Siz kutgan tinchlik va orom."},
    }
    theme = themes.get(category.slug, {'icon': '📦', 'color': '#A4D46C', 'hero': '', 'desc': ''})
    
    return TemplateResponse(request, "products/category_detail.html", {
        "base_template": _get_base_template(request),
        "category": category,
        "products": products_qs[:40],
        "theme": theme,
    })

def product_detail_view(request, uuid):
    """Mahsulot detali."""
    product = get_product_detail_selector(uuid)
    if not product: return redirect('home')
    
    increment_product_view_count_service(product=product)
    similar_products = get_similar_products_selector(product)
    nav_categories = get_root_categories_selector()
    
    return TemplateResponse(request, "product_detail_erp.html", {
        "base_template": _get_base_template(request),
        "product": product,
        "similar_products": similar_products,
        "nav_categories": nav_categories,
    })

# --- Other Pages ---

def services_view(request):
    return TemplateResponse(request, "services_erp.html", {"base_template": _get_base_template(request)})

def manufacturers_view(request):
    return TemplateResponse(request, "manufacturers_erp.html", {"base_template": _get_base_template(request)})

def company_view(request):
    return TemplateResponse(request, "company_erp.html", {"base_template": _get_base_template(request)})

def cart_view(request):
    return TemplateResponse(request, "cart_erp.html", {"base_template": _get_base_template(request)})

def wishlist_view(request):
    return TemplateResponse(request, "wishlist_erp.html", {"base_template": _get_base_template(request)})

def manufacturing_view(request):
    items = get_manufacturing_products_selector()[:20]
    return TemplateResponse(request, "manufacturing_erp.html", {
        "base_template": _get_base_template(request),
        "manufacturing_items": items,
    })

def escrow_view(request):
    return TemplateResponse(request, "escrow_erp.html", {"base_template": _get_base_template(request)})

def download_catalog(request):
    return redirect('home')

# --- User Profile & Auth Stubs (Redirect to Users App) ---

def login_view(request): return redirect('users:login')
def register_view(request): return redirect('users:register')
def logout_view(request): return redirect('users:logout')
def profile_view(request): return redirect('mgmt:profile') # Or wherever profile is
def profile_edit_view(request): return redirect('mgmt:profile_edit')
def orders_view(request): return redirect('mgmt:orders_list')
def seller_profile_view(request, username):
    from apps.users.models import User
    seller = get_object_or_404(User, username=username)
    products = get_active_products_selector().filter(seller=seller)[:20]
    return TemplateResponse(request, "seller_profile_erp.html", {
        "base_template": _get_base_template(request),
        "seller": seller,
        "products": products,
    })
def customer_register_view(request): return redirect('users:register')

# --- Admin Stubs ---

def product_admin_list_view(request): return redirect('mgmt:product-list')
def product_admin_create_view(request): return redirect('mgmt:product-create')

# --- API VIEWS ---
from rest_framework import generics, permissions
from .serializers import ProductReviewSerializer
from .models import ProductReview

class IsReviewOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class ProductReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return ProductReview.objects.filter(product__uuid=self.kwargs['uuid']).prefetch_related('images', 'user')

    def perform_create(self, serializer):
        product = get_product_detail_selector(self.kwargs['uuid'])
        serializer.save(user=self.request.user, product=product)

class ProductReviewDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewOwner]
    lookup_field = 'id'
    http_method_names = ['get', 'patch'] # Faqat GET va PATCH ruxsat etiladi


def api_products_list(request):
    from django.http import JsonResponse
    from .serializers import ProductListSerializer
    products_qs = get_active_products_selector()[:20]
    serializer = ProductListSerializer(products_qs, many=True)
    return JsonResponse(serializer.data, safe=False)

def api_product_detail(request, uuid):
    from django.http import JsonResponse
    from .serializers import ProductDetailSerializer
    product = get_product_detail_selector(uuid)
    if not product: return JsonResponse({"error": "Mahsulot topilmadi"}, status=404)
    serializer = ProductDetailSerializer(product)
    return JsonResponse(serializer.data)

def api_category_tree(request):
    from django.http import JsonResponse
    def build_tree(categories):
        result = []
        for cat in categories:
            node = {"id": cat.id, "name": cat.name_uz, "slug": cat.slug, "children": build_tree(cat.children.filter(is_active=True))}
            result.append(node)
        return result
    root_categories = Category.objects.filter(parent=None, is_active=True).prefetch_related("children")
    return JsonResponse(build_tree(root_categories), safe=False)
