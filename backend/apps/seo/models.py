"""
TZ §22 - SEO domain.
Metadata, sitemap, JSON-LD schema for all entities.
"""
from __future__ import annotations

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class SEOMetadata(BaseModel):
    """
    TZ §22 - SEO metadata for any entity (product, profile, category, page).
    Generic relation bilan har qanday modelga ulanadi.
    """
    # Generic foreign key
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content turi")
    )
    object_id = models.CharField(
        max_length=50,
        verbose_name=_("Object ID")
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # SEO fields
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Meta title")
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name=_("Meta description")
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Meta keywords")
    )

    # Open Graph
    og_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("OG title")
    )
    og_description = models.TextField(
        blank=True,
        verbose_name=_("OG description")
    )
    og_image = models.ImageField(
        upload_to="seo/og_images/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("OG image")
    )
    og_type = models.CharField(
        max_length=50,
        default="website",
        verbose_name=_("OG type")
    )

    # Twitter Card
    twitter_card = models.CharField(
        max_length=20,
        default="summary_large_image",
        verbose_name=_("Twitter card type")
    )
    twitter_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Twitter title")
    )
    twitter_description = models.TextField(
        blank=True,
        verbose_name=_("Twitter description")
    )
    twitter_image = models.ImageField(
        upload_to="seo/twitter_images/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("Twitter image")
    )

    # Technical SEO
    canonical_url = models.URLField(
        blank=True,
        verbose_name=_("Canonical URL")
    )
    noindex = models.BooleanField(
        default=False,
        verbose_name=_("Noindex?")
    )
    nofollow = models.BooleanField(
        default=False,
        verbose_name=_("Nofollow?")
    )

    # JSON-LD Schema
    schema_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Schema.org type"),
        help_text=_("Product, Service, Organization, BreadcrumbList, etc.")
    )
    schema_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("JSON-LD data")
    )

    class Meta:
        verbose_name = "SEO metadata"
        verbose_name_plural = "SEO metadatalar"
        unique_together = ["content_type", "object_id"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return f"SEO for {self.content_type} #{self.object_id}"


class SitemapURL(BaseModel):
    """
    TZ §22 - Dynamic sitemap entries.
    Auto-generated but admin can add custom.
    """
    url = models.URLField(
        unique=True,
        verbose_name=_("URL")
    )
    changefreq = models.CharField(
        max_length=20,
        choices=[
            ("always", "always"),
            ("hourly", "hourly"),
            ("daily", "daily"),
            ("weekly", "weekly"),
            ("monthly", "monthly"),
            ("yearly", "yearly"),
            ("never", "never"),
        ],
        default="weekly",
        verbose_name=_("Changefreq")
    )
    priority = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.5,
        verbose_name=_("Priority")
    )
    lastmod = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Lastmod")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol")
    )

    class Meta:
        verbose_name = "Sitemap URL"
        verbose_name_plural = "Sitemap URLlar"
        ordering = ["-priority", "url"]

    def __str__(self) -> str:
        return f"{self.url} (p:{self.priority})"


class Redirect(BaseModel):
    """
    TZ §22 - 301 redirects for slug changes.
    Admin-managed redirect table.
    """
    old_path = models.CharField(
        max_length=500,
        verbose_name=_("Eski yo'l")
    )
    new_path = models.CharField(
        max_length=500,
        verbose_name=_("Yangi yo'l")
    )
    is_permanent = models.BooleanField(
        default=True,
        verbose_name=_("Doimiy redirect? (301)")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol")
    )
    hit_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Murojaatlar soni")
    )

    class Meta:
        verbose_name = "Redirect"
        verbose_name_plural = "Redirectlar"
        unique_together = ["old_path"]
        indexes = [
            models.Index(fields=["old_path", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.old_path} → {self.new_path}"
