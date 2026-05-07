"""User & profile API views."""
from __future__ import annotations

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.contrib import messages

from .selectors import public_profile
from .models import User
from apps.products.models import Product, ProductStatus
from apps.services.models import Service
from apps.showroom.models import PortfolioItem
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


class UserProfileView(View):
    """Dynamic profile view based on user role and profession."""

    def get(self, request, username: str):
        user = get_object_or_404(
            User.objects.select_related("profile"),
            username=username,
        )

        profile = getattr(user, "profile", None)
        
        # Default template
        template_name = "profile/public_profile.html"
        
        # Role/Profession based template logic
        if user.role == "customer":
            template_name = "profile/customer.html"
        elif user.is_seller:
            professions = profile.professions if profile else []
            if "designer" in professions:
                template_name = "profile/designer.html"
            elif "master" in professions:
                template_name = "profile/master.html"
            # Add more role mappings as needed
            
        # Context data
        products = Product.objects.filter(
            seller=user,
            status=ProductStatus.PUBLISHED,
        ).select_related("category").prefetch_related("images")
        
        services = Service.objects.filter(
            provider=user,
            is_open_for_booking=True,
        )
        
        portfolio = PortfolioItem.objects.filter(
            seller=user,
            is_published=True,
        )

        context = {
            "viewed_user": user,
            "profile": profile,
            "products": products,
            "services": services,
            "portfolio": portfolio,
            "show_products": products.exists(),
            "show_portfolio": portfolio.exists(),
            "show_services": services.exists(),
            "is_owner": request.user.is_authenticated and request.user == user,
            "active_tab": request.GET.get("tab", "products"),
        }
        return TemplateResponse(request, template_name, context)


from .forms import UserUpdateForm, ProfileUpdateForm

class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Edit profile view (HTMX friendly or standard POST)."""
    template_name = "profile/edit_profile.html"

    def test_func(self):
        # Only allow users to edit their own profile
        return self.request.user.username == self.kwargs.get("username")

    def get(self, request, username):
        user = request.user
        profile = user.profile
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)
        
        context = {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile": profile,
        }
        return TemplateResponse(request, self.template_name, context)

    def post(self, request, username):
        user = request.user
        profile = user.profile
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profil muvaffaqiyatli yangilandi!")
            return redirect("users:user_profile", username=user.username)
        
        context = {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile": profile,
        }
        return TemplateResponse(request, self.template_name, context)
