"""User & profile views."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from apps.products.selectors import get_products_by_seller
from apps.services.models import Service
from apps.showroom.selectors import get_portfolio_by_seller

from .utils import get_dashboard_url

from .forms import (
    ProfileUpdateForm,
    RegisterForm,
    SellerProfileForm,
    UserUpdateForm,
)
from .models import Profile, ProfileVisibility, Role, User
from .selectors import public_profile
from .serializers import (
    ProfileSerializer,
    PublicProfileSerializer,
    UserSerializer,
)
from .services import update_profile


# ---------------------------------------------------------------------------
# DRF API views
# ---------------------------------------------------------------------------
class MeViewSet(viewsets.ViewSet):
    """`/api/v1/users/me/` — read + update the authenticated user's own data."""

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["get", "patch"], url_path="profile")
    def profile(self, request):
        if request.method == "GET":
            return Response(ProfileSerializer(request.user.profile).data)

        ser = ProfileSerializer(request.user.profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        update_profile(user=request.user, **ser.validated_data)
        request.user.refresh_from_db()
        return Response(ProfileSerializer(request.user.profile).data)


class PublicProfileView(RetrieveAPIView):
    """`/api/v1/users/u/{username}/` — JSON public profile."""

    permission_classes = [permissions.AllowAny]
    serializer_class = PublicProfileSerializer
    lookup_field = "username"

    def get_object(self):
        profile = public_profile(self.kwargs["username"])
        if not profile:
            raise NotFound("Profile not found or not public.")
        return profile


# ---------------------------------------------------------------------------
# Public profile (HTML, Instagram-style)
# ---------------------------------------------------------------------------
TAB_OVERVIEW = "overview"
TAB_PRODUCTS = "products"
TAB_SERVICES = "services"
TAB_PORTFOLIO = "portfolio"
TAB_CONTACT = "contact"


class UserProfileView(View):
    """Render `/@<username>/` and tab pages."""

    template_name = "profile/public_profile.html"

    def get(self, request, username: str, tab: str | None = None):
        user = get_object_or_404(
            User.objects.select_related("profile"),
            username__iexact=username,
            is_active=True,
        )

        profile, _ = Profile.objects.get_or_create(user=user)
        is_owner = request.user.is_authenticated and request.user.pk == user.pk

        if not is_owner and profile.visibility == ProfileVisibility.HIDDEN:
            raise Http404(_("Profile is hidden."))

        products = get_products_by_seller(user.id, only_published=not is_owner)
        portfolio = get_portfolio_by_seller(user.id, only_published=not is_owner)
        services = Service.objects.filter(provider=user)
        if not is_owner:
            services = services.filter(is_open_for_booking=True)

        counts = {
            "products": products.count(),
            "services": services.count(),
            "portfolio": portfolio.count(),
        }

        available = {
            TAB_PRODUCTS: is_owner or counts["products"] > 0,
            TAB_SERVICES: is_owner or counts["services"] > 0,
            TAB_PORTFOLIO: is_owner or counts["portfolio"] > 0,
            TAB_CONTACT: True,
        }

        active_tab = tab or request.GET.get("tab") or TAB_OVERVIEW
        if active_tab != TAB_OVERVIEW and not available.get(active_tab, False):
            active_tab = TAB_OVERVIEW

        display_name = profile.display_name or user.username

        context = {
            "viewed_user": user,
            "profile": profile,
            "primary_avatar": profile.avatars.filter(is_primary=True).first()
            or profile.avatars.first(),
            "products": products,
            "services": services,
            "portfolio_items": portfolio,
            "counts": counts,
            "available_tabs": available,
            "show_products": available[TAB_PRODUCTS],
            "show_services": available[TAB_SERVICES],
            "show_portfolio": available[TAB_PORTFOLIO],
            "is_owner": is_owner,
            "active_tab": active_tab,
            "display_name": display_name,
            "page_title": f"{display_name} (@{user.username}) — Bittada",
        }
        return TemplateResponse(request, self.template_name, context)


# ---------------------------------------------------------------------------
# Profile edit (dashboard)
# ---------------------------------------------------------------------------
class ProfileEditView(LoginRequiredMixin, View):
    """`/dashboard/profile/edit/` — edit the authenticated user's profile."""

    template_name = "profile/edit_profile.html"
    login_url = "/login/"

    def _forms(self, request, *, post=False):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if post:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(
                request.POST, request.FILES, instance=profile
            )
        else:
            user_form = UserUpdateForm(instance=request.user)
            profile_form = ProfileUpdateForm(instance=profile)
        return profile, user_form, profile_form

    def get(self, request, *args, **kwargs):
        profile, user_form, profile_form = self._forms(request)
        return TemplateResponse(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
                "profile": profile,
                "page_title": _("Profilni tahrirlash"),
            },
        )

    def post(self, request, *args, **kwargs):
        profile, user_form, profile_form = self._forms(request, post=True)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form.save()
            # Session refresh: foydalanuvchi ma'lumotlari o'zgarsa, sessiya yangilanadi
            # Bu brauzerdagi eski ma'lumotlarni yo'qotadi
            update_session_auth_hash(request, user)
            messages.success(request, _("Profil muvaffaqiyatli yangilandi."))
            return redirect("user_profile", username=request.user.username)
        return TemplateResponse(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
                "profile": profile,
                "page_title": _("Profilni tahrirlash"),
            },
        )


# ---------------------------------------------------------------------------
# Seller dashboard profile edit (legacy)
# ---------------------------------------------------------------------------
class SellerProfileEditView(LoginRequiredMixin, FormView):
    """`/dashboard/seller/profile/edit/` — seller profile editor."""

    form_class = SellerProfileForm
    template_name = "dashboard/seller/profile_edit.html"
    login_url = "/login/"
    success_url = reverse_lazy("seller:profile_edit")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not getattr(request.user, "is_seller", False):
            messages.warning(request, _("Bu sahifa faqat sotuvchilar uchun."))
            return redirect("profile")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Session yangilash — rol o'zgargan bo'lsa brauzerdagi kesh tozalanadi
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, _("Profil muvaffaqiyatli saqlandi."))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "page_title": _("Profilni tahrirlash"),
                "active_section": "profile",
                "current_user": self.request.user,
            }
        )
        return ctx


# ---------------------------------------------------------------------------
# Auth template views (register / login)
# ---------------------------------------------------------------------------
class RegisterView(FormView):
    """`/auth/register/` — Django Templates registration."""

    form_class = RegisterForm
    template_name = "auth/register.html"

    def get_success_url(self):
        return get_dashboard_url(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        django_login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(self.request, _("Akkaunt yaratildi va tizimga kirildingiz."))
        return super().form_valid(form)


class LoginView(View):
    """`/auth/login/` — Django Templates login."""

    template_name = "auth/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_dashboard_url(request.user))
        from django.conf import settings
        return render(
            request,
            self.template_name,
            {
                "page_title": _("Kirish"),
                "telegram_bot_username": getattr(settings, "TELEGRAM_BOT_USERNAME", ""),
                "google_auth_enabled": bool(getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")),
            },
        )

    def post(self, request, *args, **kwargs):
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")
        error = None

        if not identifier or not password:
            error = _("Email/username va parol kiritilishi shart.")
        else:
            user = authenticate(request, email=identifier, password=password)
            if user is None:
                try:
                    u_obj = User.objects.get(username__iexact=identifier)
                    user = authenticate(request, email=u_obj.email, password=password)
                except User.DoesNotExist:
                    user = None
            if user is None:
                error = _("Email/username yoki parol noto'g'ri.")
            else:
                django_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                # Session yangilash — oldingi sessiya ma'lumotlari tozalanadi
                update_session_auth_hash(request, user)
                messages.success(request, _("Tizimga muvaffaqiyatli kirdingiz."))

                target_url = get_dashboard_url(user)

                if request.headers.get("HX-Request"):
                    response = HttpResponse()
                    response["HX-Redirect"] = target_url
                    return response
                return redirect(target_url)

        return render(
            request,
            self.template_name,
            {
                "page_title": _("Kirish"),
                "error": error,
                "identifier": identifier,
            },
        )
