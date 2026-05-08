"""
Read queries for `products`.

Pure functions returning querysets / dicts. No side effects, no writes.
Optimize with `select_related` / `prefetch_related` here, not in views.
"""
from __future__ import annotations

from django.db.models import Count, Q, QuerySet
from .models import Category, Product, ProductStatus, ProductType

def get_root_categories_selector() -> QuerySet[Category]:
    """Asosiy kategoriyalar va ularning farzandlarini olish."""
    return Category.objects.filter(
        parent=None, 
        is_active=True
    ).prefetch_related('children').annotate(
        product_count=Count('products', filter=Q(products__status=ProductStatus.PUBLISHED))
    ).order_by('sort_order')

def get_active_products_selector() -> QuerySet[Product]:
    """Nashr etilgan va faol mahsulotlar bazaviy queryseti."""
    return Product.objects.filter(
        status=ProductStatus.PUBLISHED
    ).select_related('category', 'seller', 'seller__profile').prefetch_related('images')

def get_standard_products_selector(limit: int = 20) -> QuerySet[Product]:
    """Tayyor (Retail) mahsulotlar ro'yxati."""
    return get_active_products_selector().filter(
        product_type=ProductType.STANDARD
    ).order_by('-created_at')[:limit]

def get_manufacturing_products_selector(category_slug: str | None = None) -> QuerySet[Product]:
    """Buyurtma asosida ishlab chiqarish (B2B) mahsulotlari."""
    qs = get_active_products_selector().filter(
        product_type=ProductType.MANUFACTURING
    )
    if category_slug:
        qs = qs.filter(category__slug__iexact=category_slug)
    return qs.order_by('-created_at')

def get_product_detail_selector(uuid: str) -> Product | None:
    """Mahsulot detali barcha bog'liqliklari bilan."""
    try:
        return Product.objects.select_related(
            'category', 
            'category__parent',
            'seller', 
            'seller__profile'
        ).prefetch_related(
            'images', 
            'variants', 
            'files'
        ).get(uuid=uuid, status=ProductStatus.PUBLISHED)
    except (Product.DoesNotExist, ValueError):
        return None

def get_similar_products_selector(product: Product, limit: int = 4) -> QuerySet[Product]:
    """O'xshash mahsulotlarni topish (kategoriya bo'yicha)."""
    return get_active_products_selector().filter(
        category=product.category
    ).exclude(id=product.id).order_by('?')[:limit]
