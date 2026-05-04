"""DRF serializers for user-facing endpoints."""
from __future__ import annotations

from rest_framework import serializers

from .models import KycDocument, Profile, ProfileAvatar, User


class ProfileAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAvatar
        fields = ["id", "image", "is_primary", "order"]


class ProfileSerializer(serializers.ModelSerializer):
    avatars = ProfileAvatarSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id", "display_name", "company_name", "bio", "cover_image",
            "professions",
            "phones", "contact_email", "contact_email_visibility",
            "telegram", "website",
            "address_text", "geo_lat", "geo_lng", "working_hours",
            "visibility",
            "rating", "review_count", "profile_views",
            "avatars",
        ]
        read_only_fields = ["rating", "review_count", "profile_views", "avatars"]


class UserSerializer(serializers.ModelSerializer): # Foydalanuvchi ma'lumotlari uchun serializer
    profile = ProfileSerializer(read_only=True) # Foydalanuvchi profili (faqat o'qish uchun)

    class Meta: # Meta sozlamalari
        model = User # User modeli bilan bog'lash
        fields = [ # JSONda ko'rinadigan maydonlar ro'yxati
            "id", "email", "phone", "username", "role", "account_type",
            "is_active", "email_verified_at", "phone_verified_at", "kyc_verified_at",
            "last_seen_at", "created_at",
            "profile",
        ]
        read_only_fields = [ # O'zgartirib bo'lmaydigan maydonlar
            "id", "role", "is_active", "phone",
            "email_verified_at", "phone_verified_at", "kyc_verified_at",
            "last_seen_at", "created_at", "profile",
        ]


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Soddalashtirilgan foydalanuvchi ma'lumotlari — mahsulot kartochkalari uchun.
    Faqat public ko'rinadigan maydonlar.
    """
    display_name = serializers.CharField(source="profile.display_name", read_only=True)
    company_name = serializers.CharField(source="profile.company_name", read_only=True)
    avatar = serializers.SerializerMethodField()
    rating = serializers.DecimalField(
        source="profile.rating",
        max_digits=3,
        decimal_places=2,
        read_only=True,
    )
    review_count = serializers.IntegerField(source="profile.review_count", read_only=True)
    
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "role",
            "display_name",
            "company_name",
            "avatar",
            "rating",
            "review_count",
        ]
    
    def get_avatar(self, obj: User) -> str | None:
        primary = obj.profile.avatars.filter(is_primary=True).first()
        if not primary:
            primary = obj.profile.avatars.first()
        if primary:
            return primary.image.url
        return None


class PublicProfileSerializer(serializers.ModelSerializer):
    """The shape returned at `/u/{username}/` — strips private fields."""

    avatars = ProfileAvatarSerializer(many=True, read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "username", "role",
            "display_name", "company_name", "bio", "cover_image",
            "professions",
            "telegram", "website",
            "address_text", "geo_lat", "geo_lng", "working_hours",
            "rating", "review_count",
            "avatars",
        ]


class KycDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KycDocument
        fields = ["id", "kind", "file", "status", "note", "reviewed_at", "created_at"]
        read_only_fields = ["status", "reviewed_at", "created_at"]
