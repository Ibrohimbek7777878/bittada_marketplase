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
    
    Mebel sohasi uchun kategoriyalar:
    - Mebel (Oshxona, Yotoqxona, Mehmonxona, Bolalar, Ofis, Bog', ...)
    - Eshiklar (Kiruvchi, Xona ichki, Metaldan, ...)
    - Oynalar (Deraza, Eshik oynasi, ...)
    """
    name_uz = models.CharField(max_length=100, verbose_name=_("Nomi (O'zbek)"))
    name_ru = models.CharField(max_length=100, verbose_name=_("Nomi (Rus)"))
    name_en = models.CharField(max_length=100, verbose_name=_("Nomi (English)"))
    
    slug = models.SlugField(max_length=100, unique=True)
    
    # MPTT daraxt uchun
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
    
    # Kategoriya sozlamalari
    icon = models.ImageField(upload_to="categories/icons/", null=True, blank=True)
    cover_image = models.ImageField(upload_to="categories/covers/", null=True, blank=True)
    
    # Mahsulot turi filter
    product_type_filter = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.STANDARD,
        verbose_name=_("Mahsulot turi"),
    )
    
    # SEO
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    seo_keywords = models.CharField(max_length=500, blank=True)
    og_image = models.ImageField(upload_to="categories/og/", null=True, blank=True)
    
    # Ko'rinsh sozlamalari
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
        """Til bo'yicha nomni olish"""
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
    
    TZ §10 bo'yicha:
    - standard: zaxiradan sotiladi
    - manufacturing: MOQ/MAX bilan buyurtma
    
    Mebel sohasiga mos:
    - materials, dimensions, colors, style, condition
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Asosiy identifikatorlar
    sku = models.CharField(max_length=100, blank=True, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, db_index=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Sotuvchi
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        limit_choices_to={"role__in": ["seller", "internal_supplier"]},
    )
    
    # Turi va holati
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
    
    # Kategoriya (TZ §12)
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
    
    # Nomlar (multilingual)
    title_uz = models.CharField(max_length=200, verbose_name=_("Sarlavha (O'zbek)"))
    title_ru = models.CharField(max_length=200, verbose_name=_("Sarlavha (Rus)"), blank=True)
    title_en = models.CharField(max_length=200, verbose_name=_("Sarlavha (English)"), blank=True)
    
    # Tavsif (multilingual)
    description_uz = models.TextField(verbose_name=_("Tavsif (O'zbek)"))
    description_ru = models.TextField(blank=True, verbose_name=_("Tavsif (Rus)"))
    description_en = models.TextField(blank=True, verbose_name=_("Tavsif (English)"))
    
    # ===== MEBEL SOHASIGA MOS MAYDONLAR =====
    
    # Material (ko'p tanlash mumkin)
    materials = models.JSONField(
        default=list,
        blank=True,
        help_text="Materiallar ro'yxati (Material.choices)",
    )
    primary_material = models.CharField(
        max_length=20,
        choices=Material.choices,
        blank=True,
        verbose_name=_("Asosiy material"),
    )
    
    # O'lchamlar (sm)
    width_cm = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Eni (sm)"))
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Balandligi (sm)"))
    depth_cm = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Chuqurligi (sm)"))
    length_cm = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Uzunligi (sm)"))
    
    # Og'irlik (kg) — yetkazib berish uchun
    weight_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Og'irligi (kg)"),
    )
    
    # Ranglar (ko'p tanlash)
    colors = models.JSONField(
        default=list,
        blank=True,
        help_text="Ranglar ro'yxati (Color.choices)",
    )
    primary_color = models.CharField(
        max_length=20,
        choices=Color.choices,
        blank=True,
        verbose_name=_("Asosiy rang"),
    )
    
    # Uslub
    style = models.CharField(
        max_length=20,
        choices=Style.choices,
        blank=True,
        verbose_name=_("Uslub"),
    )
    
    # Holat
    condition = models.CharField(
        max_length=20,
        choices=Condition.choices,
        default=Condition.NEW,
        verbose_name=_("Holati"),
    )
    
    # Yozgi/bog' mebeli?
    is_outdoor = models.BooleanField(default=False, verbose_name=_("Tashqi mebel"))
    
    # Yig'iladigan/butun?
    is_assembly_required = models.BooleanField(default=True, verbose_name=_("Yig'ilishi kerak"))
    
    # ===== NARX VA ZAXIRA =====
    
    # Narxlar
    price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_("Joriy narx"),
        validators=[MinValueValidator(0)],
    )
    old_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Eski narx"),
    )
    
    # Chegirma
    discount_percent = models.PositiveSmallIntegerField(default=0)
    discount_start = models.DateTimeField(null=True, blank=True)
    discount_end = models.DateTimeField(null=True, blank=True)
    
    # Zaxira (warehouse moduli bilan integratsiya)
    stock_qty = models.PositiveIntegerField(default=0, verbose_name=_("Zaxira"))
    is_in_stock = models.BooleanField(default=True, db_index=True)
    
    # ===== BUYURTMA ASOSIDA ISHLAB CHIQARISH (Manufacturing) =====
    
    # MOQ - Minimum Order Quantity (TZ §10.1)
    moq = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Minimal buyurtma (MOQ)"),
        help_text="Eng kam buyurtma soni",
    )
    # MAX - maksimal bir martalik buyurtma
    max_qty = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Maksimal buyurtma"),
        help_text="Bir martada ko'p buyurtma mumkin (null = cheksiz)",
    )
    
    # Narx diapazoni (manufacturing uchun)
    min_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Minimal narx"),
    )
    max_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Maksimal narx"),
    )
    
    # Ishlab chiqarish vaqti (kun)
    production_time_days = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Ishlab chiqarish vaqti (kun)"),
    )
    
    # 3D Model - TZ §2.1 (GLB format)
    glb_model = models.FileField(
        upload_to="products/3d_models/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("3D Model (GLB)"),
        help_text="Mahsulotning 3D ko'rinishi uchun .glb fayli",
    )
    
    # ===== QO'SHIMCHA =====
    
    # Hashtags (qidiruv uchun)
    hashtags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Virgul bilan ajratilgan hashtaglar",
    )
    
    # Ko'rinsh sozlamalari
    is_featured = models.BooleanField(default=False, db_index=True)
    view_count = models.PositiveBigIntegerField(default=0)
    
    # SEO
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
        """Joriy narx (chegirma hisobga olingan)"""
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
    def display_dimensions(self) -> str:
        """O'lchamlar matni (masalan: '200 x 90 x 100 sm')"""
        dims = []
        if self.width_cm:
            dims.append(f"{self.width_cm}")
        if self.length_cm or self.depth_cm:
            dims.append(f"{self.length_cm or self.depth_cm}")
        if self.height_cm:
            dims.append(f"{self.height_cm}")
        return " x ".join(dims) + " sm" if dims else ""
    
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
        """Slug avtomatik yaratish"""
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


# ---------------------------------------------------------------------------
# Product Image
# ---------------------------------------------------------------------------
class ProductImage(BaseModel):
    """Mahsulot rasmlari (10 tagacha, TZ §10.2)"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/images/%Y/%m/")
    
    # Til bo'yicha alt matn
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
    
    def get_alt(self, lang: str = "uz") -> str:
        return getattr(self, f"alt_{lang}", self.alt_uz) or self.alt_uz


# ---------------------------------------------------------------------------
# Product Variant (Rang/o'lcham variantlari)
# ---------------------------------------------------------------------------
class ProductVariant(BaseModel):
    """
    Mahsulot varianti — rang yoki o'lcham bo'yicha.
    
    Masalan: "Kulrang / 200x90", "Jigarrang / 180x80"
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    
    # Variant nomi
    name_uz = models.CharField(max_length=100, verbose_name=_("Variant nomi"))
    
    # O'lchamlar (agar asosidan farq qilsa)
    width_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    depth_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    length_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Narx farqi (asosiy narxdan qo'shimcha/ayrima)
    price_adjustment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Qo'shimcha narx (+/-)"
    )
    
    # Zaxira
    stock_qty = models.PositiveIntegerField(default=0)
    
    # SKU
    sku = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = "products_product_variant"
        ordering = ["order", "created_at"]
    
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return f"{self.product.title_uz} - {self.name_uz}"
    
    @property
    def effective_price(self) -> Any:
        return self.product.price + self.price_adjustment


# ---------------------------------------------------------------------------
# Product File (blueprints, production files)
# ---------------------------------------------------------------------------
class ProductFile(BaseModel):
    """
    Mahsulot fayllari — TZ §10.2.
    
    - downloadable: public (har kim yuklab olishi mumkin)
    - production_files: xususiy (so'rov orqali)
    - blueprints: chizmalar (so'rov orqali, to'lov mumkin)
    """
    class FileType(models.TextChoices):
        DOWNLOADABLE = "downloadable", _("Yuklab olinadigan")
        PRODUCTION = "production", _("Ishlab chiqarish fayllari")
        BLUEPRINT = "blueprint", _("Chizmalar/Blueprint")
    
    class Visibility(models.TextChoices):
        PUBLIC = "public", _("Ochiq")
        ON_REQUEST = "on_request", _("So'rov orqali")
        PAID = "paid", _("To'lovli")
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="files",
    )
    
    
    file_type = models.CharField(max_length=20, choices=FileType.choices)
    visibility = models.CharField(max_length=20, choices=Visibility.choices)
    
    file = models.FileField(upload_to="products/files/%Y/%m/")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # To'lov uchun narx (agar visibility=PAID)
    unlock_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    
    # Yuklab olishlar soni
    download_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = "products_product_file"
        ordering = ["-created_at"]


class FileAccessStatus(models.TextChoices):
    """TZ §10.3 - Private file access request statuses"""
    PENDING = "pending", "Kutilmoqda"
    APPROVED = "approved", "Tasdiqlangan"
    DENIED = "denied", "Rad etildi"
    PAID_PENDING = "paid_pending", "To'lov kutilmoqda"
    PAID_APPROVED = "paid_approved", "To'lov qilindi, tasdiqlandi"
    EXPIRED = "expired", "Muddati tugagan"


class ProductFileAccessRequest(BaseModel):
    """
    TZ §10.3 - Private file access flow.
    When user requests access to a private file:
    1. Owner gets notification
    2. Owner can approve/deny/set price
    3. All actions logged in audit trail
    """
    file = models.ForeignKey(
        ProductFile,
        on_delete=models.CASCADE,
        related_name="access_requests",
        verbose_name=_("Fayl")
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="file_access_requests",
        verbose_name=_("So'rovchi")
    )

    # Request details
    message = models.TextField(
        blank=True,
        verbose_name=_("So'rov matni"),
        help_text=_("Nima uchun bu fayl kerakligi")
    )
    status = models.CharField(
        max_length=20,
        choices=FileAccessStatus.choices,
        default=FileAccessStatus.PENDING,
        verbose_name=_("Holat")
    )

    # Owner response
    owner_decision = models.CharField(
        max_length=20,
        choices=[
            ("approve", "Tasdiqlash"),
            ("deny", "Rad etish"),
            ("request_payment", "To'lov so'rash"),
        ],
        null=True,
        blank=True,
        verbose_name=_("Egasi qarori")
    )
    owner_note = models.TextField(
        blank=True,
        verbose_name=_("Egasi izohi")
    )
    requested_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("So'ralgan narx")
    )

    # Payment
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("To'langan summa")
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("To'lov vaqti")
    )

    # Access grant
    granted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Ruxsat berilgan vaqti")
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Muddati tugash vaqti")
    )
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Yuklab olishlar soni")
    )

    # Requester context for owner (TZ §10.3)
    requester_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("So'rovchi IP")
    )
    requester_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("So'rovchi joylashuvi")
    )

    class Meta:
        verbose_name = "Fayl ruxsat so'rovi"
        verbose_name_plural = "Fayl ruxsat so'rovlari"
        unique_together = ["file", "requester"]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.requester} → {self.file.name} ({self.status})"

