"""
TZ §9 - CMS Page Builder domain.
Dynamic pages with drag-drop sections.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class PageVisibility(models.TextChoices):
    """TZ §9 - Page visibility"""
    PUBLIC = "public", "Ochiq (hamma ko'radi)"
    AUTHENTICATED = "authenticated", "Faqat tizimga kirganlar"
    ROLE_RESTRICTED = "role_restricted", "Rol cheklamali"


class PageStatus(models.TextChoices):
    """TZ §9 - Page status"""
    DRAFT = "draft", "Qoralama"
    SCHEDULED = "scheduled", "Rejalashtirilgan"
    PUBLISHED = "published", "Nashr qilingan"
    ARCHIVED = "archived", "Arxivlangan"


class CMSPage(BaseModel):
    """
    TZ §9 - Dynamic CMS page builder.
    Unlimited static/CMS pages with custom URL slugs.
    """
    # Parent page for nested URLs (/services/installation)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Ota sahifa")
    )

    # URL and identification
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_("Slug / URL yo'lakchasi")
    )
    full_path = models.CharField(
        max_length=500,
        unique=True,
        verbose_name=_("To'liq yo'l"),
        help_text=_("Masalan: /services/installation")
    )

    # Content (multilingual)
    title_uz = models.CharField(
        max_length=200,
        verbose_name=_("Sarlavha (UZ)")
    )
    title_ru = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Sarlavha (RU)")
    )
    title_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Sarlavha (EN)")
    )

    # Settings
    status = models.CharField(
        max_length=20,
        choices=PageStatus.choices,
        default=PageStatus.DRAFT,
        verbose_name=_("Holat")
    )
    visibility = models.CharField(
        max_length=20,
        choices=PageVisibility.choices,
        default=PageVisibility.PUBLIC,
        verbose_name=_("Ko'rinish")
    )
    allowed_roles = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Ruxsat etilgan rollar"),
        help_text=_("[\"seller\", \"admin\"] - visibility=role_restricted uchun")
    )
    publish_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Nashr vaqti")
    )

    # Template selection
    template = models.CharField(
        max_length=50,
        choices=[
            ("default", "Standart"),
            ("landing", "Landing page"),
            ("docs", "Hujjatlar"),
            ("form", "Forma"),
        ],
        default="default",
        verbose_name=_("Shablon")
    )
    header_variant = models.CharField(
        max_length=50,
        default="default",
        verbose_name=_("Header varianti")
    )
    footer_variant = models.CharField(
        max_length=50,
        default="default",
        verbose_name=_("Footer varianti")
    )

    # Custom code (super_admin only)
    custom_css = models.TextField(
        blank=True,
        verbose_name=_("Maxsus CSS")
    )
    custom_js = models.TextField(
        blank=True,
        verbose_name=_("Maxsus JS")
    )

    # Author and meta
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_pages",
        verbose_name=_("Yaratuvchi")
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_pages",
        verbose_name=_("Oxirgi tahrirlagan")
    )

    class Meta:
        verbose_name = "CMS Sahifa"
        verbose_name_plural = "CMS Sahifalar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_path} ({self.status})"

    def get_title(self, lang: str = "uz") -> str:
        return getattr(self, f"title_{lang}", self.title_uz) or self.title_uz


class SectionType(models.TextChoices):
    """TZ §9 - Drag-drop section types"""
    HERO = "hero", "Hero block"
    BANNER = "banner", "Banner"
    TEXT_PLAIN = "text_plain", "Oddiy matn"
    TEXT_RICH = "text_rich", "Rich text (WYSIWYG)"
    PRODUCT_SLIDER = "product_slider", "Mahsulot slider"
    SERVICE_SLIDER = "service_slider", "Xizmat slider"
    CATEGORY_GRID = "category_grid", "Kategoriya grid"
    FAQ = "faq", "FAQ accordion"
    GALLERY = "gallery", "Rasm galereyasi"
    VIDEO = "video", "Video embed"
    MODEL_3D = "model_3d", "3D model (GLB)"
    HTML = "html", "Custom HTML"
    CTA = "cta", "Call-to-action"
    TESTIMONIALS = "testimonials", "Fikrlar"
    FORM = "form", "Lead capture form"


class CMSSection(BaseModel):
    """
    TZ §9 - Page sections (drag-drop).
    Each page has multiple sections, ordered.
    """
    page = models.ForeignKey(
        CMSPage,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name=_("Sahifa")
    )

    section_type = models.CharField(
        max_length=30,
        choices=SectionType.choices,
        verbose_name=_("Sektsiya turi")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Tartib")
    )

    # Section visibility (can be role-restricted)
    visibility = models.CharField(
        max_length=20,
        choices=PageVisibility.choices,
        default=PageVisibility.PUBLIC,
        verbose_name=_("Ko'rinish")
    )
    allowed_roles = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Ruxsat etilgan rollar")
    )

    # Content (JSON-based, structure depends on section_type)
    content_uz = models.JSONField(
        default=dict,
        verbose_name=_("Kontent (UZ)")
    )
    content_ru = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Kontent (RU)")
    )
    content_en = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Kontent (EN)")
    )

    # Styling
    background_color = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Fon rangi")
    )
    text_color = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Matn rangi")
    )
    padding_top = models.CharField(
        max_length=20,
        default="40px",
        verbose_name=_("Yuqori padding")
    )
    padding_bottom = models.CharField(
        max_length=20,
        default="40px",
        verbose_name=_("Pastgi padding")
    )
    is_full_width = models.BooleanField(
        default=False,
        verbose_name=_("To'liq kenglik?")
    )

    class Meta:
        verbose_name = "CMS Sektsiya"
        verbose_name_plural = "CMS Sektsiyalar"
        ordering = ["order", "created_at"]

    def __str__(self) -> str:
        return f"{self.page.full_path} - {self.get_section_type_display()} (#{self.order})"

    def get_content(self, lang: str = "uz") -> dict:
        return getattr(self, f"content_{lang}", self.content_uz) or self.content_uz


class PageRevision(BaseModel):
    """
    TZ §9 - Page versioning with auto-save.
    Every edit creates a revision.
    """
    page = models.ForeignKey(
        CMSPage,
        on_delete=models.CASCADE,
        related_name="revisions",
        verbose_name=_("Sahifa")
    )
    revision_number = models.PositiveIntegerField(
        verbose_name=_("Revisiya raqami")
    )
    data = models.JSONField(
        verbose_name=_("Sahifa ma'lumotlari (snapshot)")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Yaratuvchi")
    )
    note = models.TextField(
        blank=True,
        verbose_name=_("Izoh")
    )
    is_auto_save = models.BooleanField(
        default=False,
        verbose_name=_("Avto-saqlash?")
    )

    class Meta:
        verbose_name = "Sahifa revisiyasi"
        verbose_name_plural = "Sahifa revisiyalari"
        ordering = ["-revision_number"]
        unique_together = ["page", "revision_number"]

    def __str__(self) -> str:
        return f"{self.page.full_path} r#{self.revision_number}"


# Legacy model (keep for compatibility)
class PageContent(BaseModel):
    """
    Legacy: Simple key-value content storage.
    Kept for backward compatibility.
    """

    key = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Kontent identifikatori (masalan: nav_home)"
    )
    value = models.TextField(
        help_text="Ko'rinadigan matn yoki yozuv"
    )
    language = models.CharField(
        max_length=10,
        default='uz',
        choices=[('uz', 'Uzbek'), ('ru', 'Russian'), ('en', 'English')]
    )

    class Meta:
        db_table = "pages_content"
        unique_together = ("key", "language")
        verbose_name = "Sahifa kontenti (legacy)"
        verbose_name_plural = "Sahifa kontentlari (legacy)"

    def __str__(self) -> str:
        return f"{self.key} [{self.language}]"
