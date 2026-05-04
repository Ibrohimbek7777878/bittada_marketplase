"""
Django admin registrations for `products` — mebel marketplace.
"""
from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Category,
    Product,
    ProductFile,
    ProductImage,
    ProductVariant,
)


# ---------------------------------------------------------------------------
# Product Image Inline
# ---------------------------------------------------------------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "alt_uz", "is_primary", "order"]
    readonly_fields = ["created_at"]


# ---------------------------------------------------------------------------
# Product Variant Inline
# ---------------------------------------------------------------------------
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = [
        "name_uz",
        "sku",
        "width_cm",
        "height_cm",
        "depth_cm",
        "price_adjustment",
        "stock_qty",
        "is_active",
        "order",
    ]


# ---------------------------------------------------------------------------
# Product File Inline
# ---------------------------------------------------------------------------
class ProductFileInline(admin.TabularInline):
    model = ProductFile
    extra = 0
    fields = ["file_type", "visibility", "name", "unlock_price", "download_count"]


# ---------------------------------------------------------------------------
# Category Admin
# ---------------------------------------------------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name_uz",
        "slug",
        "level",
        "product_type_filter",
        "is_active",
        "sort_order",
        "product_count_display",
    ]
    list_filter = ["is_active", "product_type_filter", "level"]
    search_fields = ["name_uz", "name_ru", "name_en", "slug"]
    prepopulated_fields = {"slug": ("name_uz",)}
    list_editable = ["sort_order", "is_active"]
    
    fieldsets = [
        ("Asosiy", {
            "fields": [
                "name_uz", "name_ru", "name_en",
                "slug", "parent", "level",
            ]
        }),
        ("Ko'rinish", {
            "fields": ["icon", "cover_image", "is_active", "sort_order"]
        }),
        ("Sozlamalar", {
            "fields": ["product_type_filter"]
        }),
        ("SEO", {
            "fields": ["seo_title", "seo_description", "seo_keywords", "og_image"],
            "classes": ["collapse"]
        }),
    ]
    
    def product_count_display(self, obj: Category) -> int:
        return obj.products.filter(status="published").count()
    product_count_display.short_description = "Mahsulotlar soni"


# ---------------------------------------------------------------------------
# Product Admin
# ---------------------------------------------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title_uz",
        "sku",
        "seller",
        "product_type",
        "status",
        "price_display",
        "is_in_stock",
        "is_featured",
        "view_count",
        "created_at",
    ]
    list_filter = [
        "status",
        "product_type",
        "is_in_stock",
        "is_featured",
        "condition",
        "style",
        "primary_material",
        "category",
    ]
    search_fields = [
        "title_uz",
        "title_ru",
        "title_en",
        "sku",
        "hashtags",
    ]
    readonly_fields = ["uuid", "view_count", "created_at", "updated_at"]
    list_editable = ["status", "is_featured"]
    date_hierarchy = "created_at"
    
    inlines = [ProductImageInline, ProductVariantInline, ProductFileInline]
    
    fieldsets = [
        ("Asosiy ma'lumotlar", {
            "fields": [
                ("sku", "uuid"),
                "seller",
                ("product_type", "status"),
                "category",
            ]
        }),
        ("Nomlar", {
            "fields": [
                ("title_uz", "title_ru", "title_en"),
                ("description_uz", "description_ru", "description_en"),
            ]
        }),
        ("Narx va chegirma", {
            "fields": [
                ("price", "old_price"),
                ("discount_percent", "discount_start", "discount_end"),
            ]
        }),
        ("Mebel xususiyatlari", {
            "fields": [
                ("primary_material", "materials"),
                ("primary_color", "colors"),
                "style",
                "condition",
                ("is_outdoor", "is_assembly_required"),
            ]
        }),
        ("O'lchamlar va og'irlik", {
            "fields": [
                ("width_cm", "height_cm", "depth_cm", "length_cm"),
                "weight_kg",
            ]
        }),
        ("Zaxira", {
            "fields": [
                ("stock_qty", "is_in_stock"),
            ]
        }),
        ("Buyurtma ishlab chiqarish (Manufacturing)", {
            "fields": [
                ("moq", "max_qty"),
                ("min_price", "max_price"),
                "production_time_days",
            ],
            "classes": ["collapse"]
        }),
        ("SEO va qo'shimcha", {
            "fields": [
                "hashtags",
                ("seo_title", "seo_description"),
                "is_featured",
            ],
            "classes": ["collapse"]
        }),
        ("Statistika", {
            "fields": [
                "view_count",
                ("created_at", "updated_at"),
            ],
            "classes": ["collapse"]
        }),
    ]
    
    def price_display(self, obj: Product) -> str:
        return f"{int(obj.price):,}".replace(",", " ")
    price_display.short_description = "Narx"


# ---------------------------------------------------------------------------
# Product Image Admin
# ---------------------------------------------------------------------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "alt_uz", "is_primary", "order", "created_at"]
    list_filter = ["is_primary"]
    search_fields = ["product__title_uz", "alt_uz"]
    raw_id_fields = ["product"]


# ---------------------------------------------------------------------------
# Product Variant Admin
# ---------------------------------------------------------------------------
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "name_uz",
        "sku",
        "price_adjustment",
        "stock_qty",
        "is_active",
    ]
    list_filter = ["is_active"]
    search_fields = ["product__title_uz", "name_uz", "sku"]
    raw_id_fields = ["product"]


# ---------------------------------------------------------------------------
# Product File Admin
# ---------------------------------------------------------------------------
@admin.register(ProductFile)
class ProductFileAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "name",
        "file_type",
        "visibility",
        "unlock_price",
        "download_count",
    ]
    list_filter = ["file_type", "visibility"]
    search_fields = ["product__title_uz", "name"]
    raw_id_fields = ["product"]
