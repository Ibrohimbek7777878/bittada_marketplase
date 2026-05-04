"""Admin for auth method config + sessions."""
from __future__ import annotations

from django.contrib import admin

from .models import AuthMethodConfig, OtpCode, Session, SocialIdentity


@admin.register(AuthMethodConfig)
class AuthMethodConfigAdmin(admin.ModelAdmin):
    list_display = ("method", "enabled", "updated_at")
    list_editable = ("enabled",)
    list_filter = ("enabled",)


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ("target", "purpose", "method", "expires_at", "consumed_at", "attempts")
    list_filter = ("purpose", "method")
    search_fields = ("target",)
    readonly_fields = ("code_hash", "created_at", "updated_at")


@admin.register(SocialIdentity)
class SocialIdentityAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "subject", "created_at")
    list_filter = ("provider",)
    search_fields = ("user__email", "user__username", "subject")
    autocomplete_fields = ("user",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("user", "method", "ip", "geo_country", "last_seen_at", "revoked_at")
    list_filter = ("method",)
    search_fields = ("user__email", "user__username", "ip", "user_agent")
    autocomplete_fields = ("user",)
