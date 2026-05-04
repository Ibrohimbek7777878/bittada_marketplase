"""Django admin for users domain."""
from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from django.contrib.auth.forms import AuthenticationForm
from .models import KycDocument, PermissionGrant, Profile, ProfileAvatar, User

class UserAdminAuthenticationForm(AuthenticationForm):
    """Admin login formasi email bilan ishlashini ta'minlash uchun."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].label = "Email"
            self.fields['username'].widget.attrs['placeholder'] = "admin@bittada.com"

# Admin panelning login formasini almashtirish
admin.site.login_form = UserAdminAuthenticationForm


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Custom UserAdmin that avoids DjangoUserAdmin's 'username' assumptions.
    Since we use email as the USERNAME_FIELD, we want the admin to reflect that.
    """
    list_display = ("id", "get_full_name", "phone", "role", "get_orders_count", "is_active", "created_at")
    list_filter = ("role", "account_type", "is_active", "is_staff")
    search_fields = ("id", "email", "username", "phone", "profile__display_name")
    ordering = ("-created_at",)
    
    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Identity", {"fields": ("username", "phone", "role", "account_type")}),
        ("Verification", {"fields": ("email_verified_at", "phone_verified_at", "kyc_verified_at")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("last_login", "last_seen_at", "created_at")}),
    )
    
    readonly_fields = ("id", "last_login", "last_seen_at", "created_at")

    def get_full_name(self, obj):
        return obj.profile.display_name if hasattr(obj, 'profile') else obj.username
    get_full_name.short_description = "Ism"

    def get_orders_count(self, obj):
        from apps.orders.models import Order
        if obj.role == 'customer':
            count = obj.customer_orders.count()
        else:
            count = obj.seller_orders.count()
        return f"{count} ta buyurtma"
    get_orders_count.short_description = "Buyurtmalar"
    
    # Optional: custom password save logic if needed, but set_password is usually handled by the model or management command



class ProfileAvatarInline(admin.TabularInline):
    model = ProfileAvatar
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "company_name", "visibility", "rating", "review_count")
    list_filter = ("visibility",)
    search_fields = ("user__username", "user__email", "display_name", "company_name")
    inlines = [ProfileAvatarInline]


@admin.register(KycDocument)
class KycDocumentAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "status", "reviewed_by", "reviewed_at", "created_at")
    list_filter = ("kind", "status")
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user", "reviewed_by")


@admin.register(PermissionGrant)
class PermissionGrantAdmin(admin.ModelAdmin):
    list_display = ("user", "action_key", "allowed", "note", "created_at")
    list_filter = ("allowed",)
    search_fields = ("user__username", "user__email", "action_key")
    autocomplete_fields = ("user",)
