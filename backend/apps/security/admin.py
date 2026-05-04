"""Admin views for security artefacts."""
from __future__ import annotations

from django.contrib import admin

from .models import AuditLog, IpBlock, RequestLog


@admin.register(IpBlock)
class IpBlockAdmin(admin.ModelAdmin):
    list_display = ("ip", "reason", "until", "created_by", "created_at")
    list_filter = ("until",)
    search_fields = ("ip", "reason")
    autocomplete_fields = ("created_by",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "target_type", "target_id", "ip")
    list_filter = ("action",)
    search_fields = ("actor__email", "actor__username", "action", "target_id", "ip")
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request) -> bool:  # type: ignore[no-untyped-def]
        return False

    def has_change_permission(self, request, obj=None) -> bool:  # type: ignore[no-untyped-def]
        return False

    def has_delete_permission(self, request, obj=None) -> bool:  # type: ignore[no-untyped-def]
        return False


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "method", "path", "status_code", "ip", "user", "duration_ms")
    list_filter = ("method", "status_code")
    search_fields = ("path", "ip", "user__email", "user__username")
    readonly_fields = [f.name for f in RequestLog._meta.fields]
