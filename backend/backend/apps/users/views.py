"""User & profile API views."""
from __future__ import annotations

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from .selectors import public_profile
from .serializers import (
    ProfileSerializer,
    PublicProfileSerializer,
    UserSerializer,
)
from .services import update_profile


class MeViewSet(viewsets.ViewSet):
    """`/api/v1/users/me/` — read + update the authenticated user's own data."""

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):  # type: ignore[no-untyped-def]
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["get", "patch"], url_path="profile")
    def profile(self, request):  # type: ignore[no-untyped-def]
        if request.method == "GET":
            return Response(ProfileSerializer(request.user.profile).data)

        ser = ProfileSerializer(request.user.profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        update_profile(user=request.user, **ser.validated_data)
        request.user.refresh_from_db()
        return Response(ProfileSerializer(request.user.profile).data)


class PublicProfileView(RetrieveAPIView):
    """`/api/v1/users/u/{username}/` — public seller/supplier profile."""

    permission_classes = [permissions.AllowAny]
    serializer_class = PublicProfileSerializer
    lookup_field = "username"

    def get_object(self):  # type: ignore[no-untyped-def]
        profile = public_profile(self.kwargs["username"])
        if not profile:
            raise NotFound("Profile not found or not public.")
        return profile
