"""
Products domain — mebel marketplace uchun mahsulot modellari.

TZ §10 bo'yicha:
- standard: tayyor mahsulot, zaxiradan sotiladi
- manufacturing: buyurtma asosida ishlab chiqarish (MOQ/MAX)
- service: xizmatlar (alohida app'da)

Mebel sohasiga mos qo'shimcha:
- materials: material (taxta, MDF, massiv, metall, ...)
- dimensions: o'lchamlar (eni x uzunligi x balandligi)
- colors: ranglar (multi-select)
- style: uslub (zamonaviy, klassik, skandinav, ...)
- condition: holati (yangi, foydalanilgan, restavratsiya)
"""
from __future__ import annotations

import uuid
from typing import Any

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import AuditableModel, BaseModel, SoftDeleteModel


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------
class ProductType(models.TextChoices):
    """Mahsulot turlari — TZ §10.1"""
    STANDARD = "standard", _("Tayyor mahsulot")
    MANUFACTURING = "manufacturing", _("Buyurtma asosida ishlab chiqarish")

class ProductStatus(models.TextChoices):
    """Moderatsiya holati"""
    DRAFT = "draft", _("Qoralama")
    PENDING = "pending", _("Tekshirilmoqda")
    PUBLISHED = "published", _("Faol")
    REJECTED = "rejected", _("Rad etildi")
    ARCHIVED = "archived", _("Arxiv")


class Condition(models.TextChoices):
    """Mahsulot holati — mebel sohasi uchun"""
    NEW = "new", _("Yangi")
    USED = "used", _("Foydalanilgan")
    REFURBISHED = "refurbished", _("Restavratsiya qilingan")
    ANTIQUE = "antique", _("Antikvar")


class Style(models.TextChoices):
    """Mebel uslublari"""
    MODERN = "modern", _("Zamonaviy")
    CLASSIC = "classic", _("Klassik")
    SCANDINAVIAN = "scandinavian", _("Skandinav")
    LOFT = "loft", _("Loft")
    MINIMALISM = "minimalism", _("Minimalizm")
    HIGH_TECH = "high_tech", _("High-tech")
    PROVENCE = "provence", _("Provans")
    ECO = "eco", _("Eco")
    VINTAGE = "vintage", _("Vintage")
    ORIENTAL = "oriental", _("Sharq uslubi")
    OTHER = "other", _("Boshqa")


class Material(models.TextChoices):
    """Mebel materiallari"""
    SOLID_WOOD = "solid_wood", _("Tabiiy yog'och (massiv)")
    MDF = "mdf", _("MDF")
    CHIPBOARD = "chipboard", _("LDSP (yirik hissali)")
    PLYWOOD = "plywood", _("Fanera")
    METAL = "metal", _("Metall")
    GLASS = "glass", _("Shisha")
    PLASTIC = "plastic", _("Plastik")
    RATTAN = "rattan", _("Rattan")
    LEATHER = "leather", _("Charm (haqiqiy)")
    ECO_LEATHER = "eco_leather", _("Eko-charm")
    FABRIC = "fabric", _("Mato")
    VELVET = "velvet", _("Barxat")
    MARBLE = "marble", _("Mramor")
    GRANITE = "granite", _("Granit")
    STONE = "stone", _("Tosh")
    OTHER = "other", _("Boshqa")


class Color(models.TextChoices):
    """Mebel ranglari"""
    WHITE = "white", _("Oq")
    BLACK = "black", _("Qora")
    GRAY = "gray", _("Kulrang")
    BEIGE = "beige", _("Bej")
    BROWN = "brown", _("Jigarrang")
    WALNUT = "walnut", _("Yong'oq rang")
    OAK = "oak", _("Eshak terisi rang")
    CHERRY = "cherry", _("Gilos rang")
    MAHOGANY = "mahogany", _("Kizil-yashil")
    RED = "red", _("Qizil")
    BLUE = "blue", _("Ko'k")
    GREEN = "green", _("Yashil")
    YELLOW = "yellow", _("Sariq")
    ORANGE = "orange", _("To'q sariq")
    PINK = "pink", _("Pushti")
    PURPLE = "purple", _("Siyohrang")
    GOLD = "gold", _("Oltin")
    SILVER = "silver", _("Kumush")
    MULTI = "multi", _("Ko'p rangli")
    TRANSPARENT = "transparent", _("Shaffof")
    OTHER = "other", _("Boshqa")


# ---------------------------------------------------------------------------
# Category (MPTT daraxt)
# ---------------------------------------------------------------------------
class Category(BaseModel, SoftDeleteModel):
    """
    Kategoriya daraxti — TZ §12.
    """
    name_uz = models.CharField(max_length=100, verbose_name=_("Nomi (O'zbek)"))
    name_ru = models.CharField(max_length=100, verbose_name=_("Nomi (Rus)"))
    name_en = models.CharField(max_length=100, verbose_name=_("Nomi (English)"))
    
    slug = models.SlugField(max_length=100, unique=True)
    
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    level = models.PositiveSmallIntegerField(default=0, db_index=True)
    lft = models.PositiveIntegerField(default=0, db_index=True)
    rght = models.PositiveIntegerField(default=0, db_index=True)
    tree_id = models.PositiveIntegerField(default=0, db_index=True)
    
    icon = models.ImageField(upload_to="categories/icons/", null=True, blank=True)
    cover_image = models.ImageField(upload_to="categories/covers/", null=True, blank=True)
    
    product_type_filter = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.STANDARD,
        verbose_name=_("Mahsulot turi"),
    )
    
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    seo_keywords = models.CharField(max_length=500, blank=True)
    og_image = models.ImageField(upload_to="categories/og/", null=True, blank=True)
    
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        db_table = "products_category"
        ordering = ["tree_id", "lft"]
        verbose_name = _("Kategoriya")
        verbose_name_plural = _("Kategoriyalar")
    
    def __str__(self) -> str:
        return self.name_uz
    
    def get_name(self, lang: str = "uz") -> str:
        return getattr(self, f"name_{lang}", self.name_uz) or self.name_uz
    
    @property
    def is_leaf(self) -> bool:
        return not self.children.exists()


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------
class Product(AuditableModel, SoftDeleteModel):
    """
    Mahsulot — mebel marketplace asosi.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    sku = models.CharField(max_length=100, blank=True, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, db_index=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        limit_choices_to={
            "role__in": [
                "seller", "internal_supplier", 
                "seller_retail", "seller_manufacturer", "seller_logistics", "seller_component",
                "partner_material", "partner_service",
                "designer_interior", "designer_3d",
                "fixer_master", "fixer_repair"
            ]
        },
    )
    
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.STANDARD,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
        db_index=True,
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    subcategory_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Kategoriya daraxt yo'li (denormalized)",
    )
    
    title_uz = models.CharField(max_length=200, verbose_name=_("Sarlavha (O'zbek)"))
    title_ru = models.CharField(max_length=200, verbose_name=_("Sarlavha (Rus)"), blank=True)
    title_en = models.CharField(max_length=200, verbose_name=_("Sarlavha (English)"), blank=True)
    
    description_uz = models.TextField(verbose_name=_("Tavsif (O'zbek)"))
    description_ru = models.TextField(blank=True, verbose_name=_("Tavsif (Rus)"))
    description_en = models.TextField(blank=True, verbose_name=_("Tavsif (English)"))
    
    materials = models.JSONField(default=list, blank=True)
    primary_material = models.CharField(max_length=20, choices=Material.choices, blank=True)
    
    width_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    depth_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    length_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    colors = models.JSONField(default=list, blank=True)
    primary_color = models.CharField(max_length=20, choices=Color.choices, blank=True)
    
    style = models.CharField(max_length=20, choices=Style.choices, blank=True)
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.NEW)
    
    is_outdoor = models.BooleanField(default=False)
    is_assembly_required = models.BooleanField(default=True)
    
    price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    old_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    
    discount_percent = models.PositiveSmallIntegerField(default=0)
    discount_start = models.DateTimeField(null=True, blank=True)
    discount_end = models.DateTimeField(null=True, blank=True)
    
    stock_qty = models.PositiveIntegerField(default=0)
    is_in_stock = models.BooleanField(default=True, db_index=True)
    
    moq = models.PositiveIntegerField(default=1)
    max_qty = models.PositiveIntegerField(null=True, blank=True)
    
    min_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    
    production_time_days = models.PositiveSmallIntegerField(null=True, blank=True)
    
    glb_model = models.FileField(upload_to="products/3d_models/%Y/%m/", null=True, blank=True)
    hashtags = models.CharField(max_length=500, blank=True)
    
    # Ko'rinsh sozlamalari
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_("Faol"))
    is_featured = models.BooleanField(default=False, db_index=True, verbose_name=_("Tanlangan"))
    view_count = models.PositiveBigIntegerField(default=0)
    
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    
    class Meta:
        db_table = "products_product"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "is_in_stock"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["seller", "status"]),
            models.Index(fields=["product_type", "status"]),
            models.Index(fields=["is_featured", "created_at"]),
            models.Index(fields=["style", "status"]),
            models.Index(fields=["condition", "status"]),
        ]
        verbose_name = _("Mahsulot")
        verbose_name_plural = _("Mahsulotlar")
    
    def __str__(self) -> str:
        return self.title_uz
    
    def get_title(self, lang: str = "uz") -> str:
        return getattr(self, f"title_{lang}", self.title_uz) or self.title_uz
    
    def get_description(self, lang: str = "uz") -> str:
        return getattr(self, f"description_{lang}", self.description_uz) or self.description_uz
    
    @property
    def effective_price(self) -> Any:
        from django.utils import timezone
        now = timezone.now()
        if (
            self.discount_percent > 0
            and self.discount_start
            and self.discount_end
            and self.discount_start <= now <= self.discount_end
        ):
            return self.price * (100 - self.discount_percent) / 100
        return self.price
    
    @property
    def is_discount_active(self) -> bool:
        from django.utils import timezone
        now = timezone.now()
        return (
            self.discount_percent > 0
            and self.discount_start
            and self.discount_end
            and self.discount_start <= now <= self.discount_end
        )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title_uz)[:200]
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/images/%Y/%m/")
    alt_uz = models.CharField(max_length=200, blank=True)
    alt_ru = models.CharField(max_length=200, blank=True)
    alt_en = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        db_table = "products_product_image"
        ordering = ["order", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=models.Q(is_primary=True),
                name="uniq_primary_image_per_product",
            ),
        ]


class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name_uz = models.CharField(max_length=100, verbose_name=_("Variant nomi"))
    width_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    depth_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    length_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_qty = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "products_product_variant"
        ordering = ["order", "created_at"]


class ProductFile(BaseModel):
    class FileType(models.TextChoices):
        DOWNLOADABLE = "downloadable", _("Yuklab olinadigan")
        PRODUCTION = "production", _("Ishlab chiqarish fayllari")
        BLUEPRINT = "blueprint", _("Chizmalar/Blueprint")
    
    class Visibility(models.TextChoices):
        PUBLIC = "public", _("Ochiq")
        ON_REQUEST = "on_request", _("So'rov orqali")
        PAID = "paid", _("To'lovli")
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="files")
    file_type = models.CharField(max_length=20, choices=FileType.choices)
    visibility = models.CharField(max_length=20, choices=Visibility.choices)
    file = models.FileField(upload_to="products/files/%Y/%m/")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    unlock_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = "products_product_file"
        ordering = ["-created_at"]
