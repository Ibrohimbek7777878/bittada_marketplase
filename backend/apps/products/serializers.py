"""
DRF serializers for `products` — mebel marketplace uchun.

TZ §10, §12 bo'yicha product va category API shakllari.
"""
from __future__ import annotations

from rest_framework import serializers

from apps.users.serializers import UserPublicSerializer
from .models import (
    Category,
    Color,
    Condition,
    Material,
    Product,
    ProductFile,
    ProductImage,
    ProductReview,
    ProductReviewImage,
    ProductStatus,
    ProductType,
    ProductVariant,
    Style,
)


# ---------------------------------------------------------------------------
# Category Serializers
# ---------------------------------------------------------------------------
class CategoryListSerializer(serializers.ModelSerializer):
    """Kategoriya ro'yxati uchun (tree)"""
    name = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            "id",
            "slug",
            "name",
            "level",
            "icon",
            "cover_image",
            "is_active",
            "sort_order",
            "children",
            "product_count",
        ]
    
    def get_name(self, obj: Category) -> str:
        lang = self.context.get("lang", "uz")
        return obj.get_name(lang)
    
    def get_children(self, obj: Category):
        if hasattr(obj, "cached_children"):
            children = obj.cached_children
        else:
            children = obj.children.filter(is_active=True)
        return CategoryListSerializer(children, many=True, context=self.context).data


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Kategoriya detali uchun"""
    name = serializers.SerializerMethodField()
    seo_title = serializers.SerializerMethodField()
    seo_description = serializers.SerializerMethodField()
    parent = CategoryListSerializer(read_only=True)
    breadcrumbs = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            "id",
            "slug",
            "name",
            "icon",
            "cover_image",
            "product_type_filter",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "og_image",
            "parent",
            "breadcrumbs",
            "is_active",
        ]
    
    def get_name(self, obj: Category) -> str:
        lang = self.context.get("lang", "uz")
        return obj.get_name(lang)
    
    def get_seo_title(self, obj: Category) -> str:
        return obj.seo_title or obj.name_uz
    
    def get_seo_description(self, obj: Category) -> str:
        return obj.seo_description or ""
    
    def get_breadcrumbs(self, obj: Category):
        """Kategoriya daraxt yo'li"""
        crumbs = []
        current = obj
        while current:
            crumbs.append({
                "id": str(current.id),
                "slug": current.slug,
                "name": current.get_name(self.context.get("lang", "uz")),
            })
            current = current.parent
        return list(reversed(crumbs))


# ---------------------------------------------------------------------------
# Product Image & File Serializers
# ---------------------------------------------------------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    """Mahsulot rasmi"""
    alt = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ["id", "url", "thumbnail", "alt", "order", "is_primary"]
    
    def get_alt(self, obj: ProductImage) -> str:
        lang = self.context.get("lang", "uz")
        return obj.get_alt(lang)
    
    def get_url(self, obj: ProductImage) -> str | None:
        if obj.image:
            return obj.image.url
        return None
    
    def get_thumbnail(self, obj: ProductImage) -> str | None:
        # Keyinchalik thumbnail generation qo'shiladi
        if obj.image:
            return obj.image.url
        return None


class ProductFileSerializer(serializers.ModelSerializer):
    """Mahsulot fayli (blueprint, production)"""
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductFile
        fields = [
            "id",
            "file_type",
            "visibility",
            "name",
            "description",
            "unlock_price",
            "download_count",
            "file_url",
        ]
    
    def get_file_url(self, obj: ProductFile) -> str | None:
        # Public fayllar uchun to'g'ridan-to'g'ri URL
        if obj.visibility == ProductFile.Visibility.PUBLIC:
            if obj.file:
                return obj.file.url
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    """Mahsulot varianti (rang/o'lcham)"""
    price = serializers.DecimalField(
        source="effective_price",
        max_digits=14,
        decimal_places=2,
        read_only=True,
    )
    dimensions = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "name_uz",
            "sku",
            "dimensions",
            "price",
            "price_adjustment",
            "stock_qty",
            "is_active",
        ]
    
    def get_dimensions(self, obj: ProductVariant) -> dict:
        return {
            "width_cm": obj.width_cm,
            "height_cm": obj.height_cm,
            "depth_cm": obj.depth_cm,
            "length_cm": obj.length_cm,
        }


# ---------------------------------------------------------------------------
# Product Serializers
# ---------------------------------------------------------------------------
class ProductListSerializer(serializers.ModelSerializer):
    """
    Mahsulotlar ro'yxati uchun (shop, category, search).
    Yengil serializer — tez yuklash uchun.
    """
    title = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    category = CategoryListSerializer(read_only=True)
    seller = UserPublicSerializer(read_only=True)
    price_display = serializers.SerializerMethodField()
    old_price_display = serializers.SerializerMethodField()
    is_discount_active = serializers.BooleanField(read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    dimensions_short = serializers.SerializerMethodField()
    
    # Mebel sohasiga mos
    primary_material_display = serializers.SerializerMethodField()
    primary_color_display = serializers.SerializerMethodField()
    style_display = serializers.SerializerMethodField()
    condition_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            "id",
            "uuid",
            "sku",
            "slug",  # keyinchalik qo'shiladi
            "title",
            "product_type",
            "category",
            "seller",
            "primary_image",
            "price",
            "price_display",
            "old_price",
            "old_price_display",
            "is_discount_active",
            "discount_percent",
            "is_in_stock",
            "dimensions_short",
            "primary_material",
            "primary_material_display",
            "primary_color",
            "primary_color_display",
            "style",
            "style_display",
            "condition",
            "condition_display",
            "is_featured",
            "view_count",
            "created_at",
        ]
    
    def get_title(self, obj: Product) -> str:
        lang = self.context.get("lang", "uz")
        return obj.get_title(lang)
    
    def get_primary_image(self, obj: Product):
        primary = obj.images.filter(is_primary=True).first()
        if not primary:
            primary = obj.images.first()
        if primary:
            return ProductImageSerializer(primary, context=self.context).data
        return None
    
    def get_price_display(self, obj: Product) -> str:
        """Formatlangan narx (so'm)"""
        price = obj.effective_price
        return f"{int(price):,}".replace(",", " ")
    
    def get_old_price_display(self, obj: Product) -> str | None:
        if obj.old_price:
            return f"{int(obj.old_price):,}".replace(",", " ")
        return None
    
    def get_dimensions_short(self, obj: Product) -> str:
        return obj.display_dimensions
    
    def get_primary_material_display(self, obj: Product) -> str:
        if obj.primary_material:
            return dict(Material.choices).get(obj.primary_material, obj.primary_material)
        return ""
    
    def get_primary_color_display(self, obj: Product) -> str:
        if obj.primary_color:
            return dict(Color.choices).get(obj.primary_color, obj.primary_color)
        return ""
    
    def get_style_display(self, obj: Product) -> str:
        if obj.style:
            return dict(Style.choices).get(obj.style, obj.style)
        return ""
    
    def get_condition_display(self, obj: Product) -> str:
        return dict(Condition.choices).get(obj.condition, obj.condition)


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Mahsulot detali — to'liq ma'lumot.
    """
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    category = CategoryDetailSerializer(read_only=True)
    seller = UserPublicSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    files = ProductFileSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    # Narx
    effective_price = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        read_only=True,
    )
    price_display = serializers.SerializerMethodField()
    old_price_display = serializers.SerializerMethodField()
    
    # O'lchamlar
    dimensions = serializers.SerializerMethodField()
    
    # Mebel sohasiga mos
    materials_display = serializers.SerializerMethodField()
    colors_display = serializers.SerializerMethodField()
    style_display = serializers.SerializerMethodField()
    condition_display = serializers.SerializerMethodField()
    
    # SEO
    seo_title = serializers.SerializerMethodField()
    seo_description = serializers.SerializerMethodField()
    
    # Status
    status_display = serializers.SerializerMethodField()
    product_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            # Asosiy
            "id",
            "uuid",
            "sku",
            "title",
            "description",
            "product_type",
            "product_type_display",
            "status",
            "status_display",
            
            # Bog'lanishlar
            "category",
            "seller",
            "subcategory_path",
            
            # Media
            "images",
            "files",
            "variants",
            
            # Narx
            "price",
            "price_display",
            "effective_price",
            "old_price",
            "old_price_display",
            "discount_percent",
            "discount_start",
            "discount_end",
            "is_discount_active",
            
            # Zaxira
            "stock_qty",
            "is_in_stock",
            
            # Buyurtma ishlab chiqarish
            "moq",
            "max_qty",
            "min_price",
            "max_price",
            "production_time_days",
            
            # Mebel sohasiga mos
            "materials",
            "materials_display",
            "primary_material",
            "colors",
            "colors_display",
            "primary_color",
            "style",
            "style_display",
            "condition",
            "condition_display",
            "width_cm",
            "height_cm",
            "depth_cm",
            "length_cm",
            "dimensions",
            "weight_kg",
            "is_outdoor",
            "is_assembly_required",
            
            # Hashtags
            "hashtags",
            
            # SEO
            "seo_title",
            "seo_description",
            
            # Meta
            "view_count",
            "is_featured",
            "created_at",
            "updated_at",
        ]
    
    def get_title(self, obj: Product) -> str:
        lang = self.context.get("lang", "uz")
        return obj.get_title(lang)
    
    def get_description(self, obj: Product) -> str:
        lang = self.context.get("lang", "uz")
        return obj.get_description(lang)
    
    def get_price_display(self, obj: Product) -> str:
        price = obj.effective_price
        return f"{int(price):,}".replace(",", " ")
    
    def get_old_price_display(self, obj: Product) -> str | None:
        if obj.old_price:
            return f"{int(obj.old_price):,}".replace(",", " ")
        return None
    
    def get_dimensions(self, obj: Product) -> dict:
        return {
            "width_cm": obj.width_cm,
            "height_cm": obj.height_cm,
            "depth_cm": obj.depth_cm,
            "length_cm": obj.length_cm,
            "display": obj.display_dimensions,
        }
    
    def get_materials_display(self, obj: Product) -> list:
        material_dict = dict(Material.choices)
        return [
            {"value": m, "label": material_dict.get(m, m)}
            for m in (obj.materials or [])
        ]
    
    def get_colors_display(self, obj: Product) -> list:
        color_dict = dict(Color.choices)
        return [
            {"value": c, "label": color_dict.get(c, c)}
            for c in (obj.colors or [])
        ]
    
    def get_style_display(self, obj: Product) -> str:
        if obj.style:
            return dict(Style.choices).get(obj.style, obj.style)
        return ""
    
    def get_condition_display(self, obj: Product) -> str:
        return dict(Condition.choices).get(obj.condition, obj.condition)
    
    def get_seo_title(self, obj: Product) -> str:
        return obj.seo_title or obj.get_title("uz")
    
    def get_seo_description(self, obj: Product) -> str:
        return obj.seo_description or obj.get_description("uz")[:160]
    
    def get_status_display(self, obj: Product) -> str:
        return dict(ProductStatus.choices).get(obj.status, obj.status)
    
    def get_product_type_display(self, obj: Product) -> str:
        return dict(ProductType.choices).get(obj.product_type, obj.product_type)


# ---------------------------------------------------------------------------
# Filter va Search
# ---------------------------------------------------------------------------
class ProductFilterOptionsSerializer(serializers.Serializer):
    """Mahsulot filtrlari uchun mavjud variantlar"""
    materials = serializers.ListField(child=serializers.DictField())
    colors = serializers.ListField(child=serializers.DictField())
    styles = serializers.ListField(child=serializers.DictField())
    conditions = serializers.ListField(child=serializers.DictField())
    price_range = serializers.DictField()
    categories = serializers.ListField(child=serializers.DictField())


class ProductSearchSerializer(serializers.Serializer):
    """Qidiruv natijalari"""
    query = serializers.CharField()
    results = ProductListSerializer(many=True)
    total = serializers.IntegerField()
    filters = ProductFilterOptionsSerializer()


# ---------------------------------------------------------------------------
# Review Serializers
# ---------------------------------------------------------------------------
class ProductReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReviewImage
        fields = ["id", "image"]

class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    images = ProductReviewImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ["id", "user", "product", "rating", "text", "images", "created_at"]
        read_only_fields = ["id", "user", "product", "created_at"]

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Reyting 1 dan 5 gacha bo'lishi kerak.")
        return value

