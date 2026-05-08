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
from .services import (
    update_profile, 
    create_user_with_profile, 
    initiate_multi_step_login, 
    update_user_last_login
)
from core.exceptions import DomainError
from .models import Role, AccountType
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login, logout


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


# ============================================================================
# TEMPLATE VIEWS (Professionalized)
# ============================================================================

class LoginView(View):
    """Handles multi-step login matching `login_erp.html`."""
    template_name = "login_erp.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request):
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, email=identifier, password=password)
        if not user:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user_obj = User.objects.get(phone=identifier)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass

        if user and user.is_active:
            result = initiate_multi_step_login(user)
            if result["step"] == "otp_required":
                request.session["pre_auth_user_id"] = str(user.id)
                return Response({
                    "success": True, 
                    "step": "otp", 
                    "target": result["target"],
                    "message": "OTP kod yuborildi."
                })
            
            login(request, user)
            update_user_last_login(user)
            
            redirect_url = "/"
            if user.is_staff: redirect_url = "/hidden-core-database/"
            elif user.role == Role.CUSTOMER: redirect_url = "/profile/"
            
            return Response({"success": True, "redirect": redirect_url})

        return Response({
            "success": False, 
            "message": "Email/Username yoki parol noto'g'ri."
        }, status=400)


class RegisterView(View):
    """Handles 3-step registration matching `register_erp.html`."""
    template_name = "register_erp.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request):
        data = request.POST
        try:
            user = create_user_with_profile(
                email=data.get("email") or None,
                phone=data.get("phone") or None,
                password=data.get("password"),
                first_name=data.get("first_name", ""),
                username=data.get("username"),
                role=data.get("role", Role.CUSTOMER),
                account_type=data.get("account_type", AccountType.INDIVIDUAL),
                professions=data.get("professions", "").split(",") if data.get("professions") else None,
            )
            
            login(request, user)
            update_user_last_login(user)

            redirect_url = "/"
            if user.role == Role.SELLER: redirect_url = "/services/"
            elif user.role in {Role.CUSTOMER, Role.INTERNAL_SUPPLIER}: redirect_url = "/profile/"
            
            return Response({"success": True, "redirect": redirect_url})

        except DomainError as e:
            return Response({"success": False, "message": str(e)}, status=400)
        except Exception as e:
            return Response({"success": False, "message": "Kutilmagan xatolik yuz berdi."}, status=500)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")
