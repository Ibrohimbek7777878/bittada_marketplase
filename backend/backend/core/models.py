"""
Shared base model classes.

Every domain model should inherit from one of these so we get consistent
audit columns, soft-delete semantics, and stable public identifiers.
"""
from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """Adds `created_at` / `updated_at` to any model."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDPrimaryKeyModel(models.Model):
    """Use a UUID as the public primary key — safer than incrementing IDs."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """Excludes soft-deleted rows from default queries; explicit opt-in to see them."""

    def alive(self) -> "SoftDeleteQuerySet":
        return self.filter(deleted_at__isnull=True)

    def dead(self) -> "SoftDeleteQuerySet":
        return self.filter(deleted_at__isnull=False)

    def delete(self) -> tuple[int, dict[str, int]]:
        # Soft-delete in bulk; preserves audit history but removes from listings.
        return self.update(deleted_at=timezone.now()), {}


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):  # type: ignore[misc]
    def get_queryset(self) -> SoftDeleteQuerySet:
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    """Mixin for soft-deletable rows."""

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteQuerySet.as_manager()  # includes deleted

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):  # type: ignore[no-untyped-def]
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):  # type: ignore[no-untyped-def]
        return super().delete(using=using, keep_parents=keep_parents)


class BaseModel(UUIDPrimaryKeyModel, TimestampedModel):
    """Default base — UUID id, created_at, updated_at. Use this for most domain rows."""

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class AuditableModel(BaseModel):
    """Adds `created_by` / `updated_by` references for sensitive domains."""

    created_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        editable=False,
    )
    updated_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        editable=False,
    )

    class Meta:
        abstract = True
