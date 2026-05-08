"""
User & Auth views — professionalized for Django 5 & multi-step flows.
Matches `login_erp.html` and `register_erp.html`.
"""
from __future__ import annotations

from typing import Any
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views import View
from django.http import JsonResponse
from django.conf import settings

from core.exceptions import DomainError
from .models import Role, AccountType
from .services import create_user_with_profile, initiate_multi_step_login, update_user_last_login


class LoginView(View):
    """
    Handles multi-step login. 
    Step 1: Credentials. Step 2 (optional): OTP.
    """
    template_name = "login_erp.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request):
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Authentication logic (Email or Phone)
        user = authenticate(request, email=identifier, password=password)
        if not user:
            # Fallback for phone-based login if not handled by custom backend
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user_obj = User.objects.get(phone=identifier)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass

        if user and user.is_active:
            # Check if multi-step (OTP) is needed
            result = initiate_multi_step_login(user)
            
            if result["step"] == "otp_required":
                request.session["pre_auth_user_id"] = str(user.id)
                return JsonResponse({
                    "success": True, 
                    "step": "otp", 
                    "target": result["target"],
                    "message": "OTP kod yuborildi."
                })
            
            # Direct login
            login(request, user)
            update_user_last_login(user)
            
            redirect_url = "/"
            if user.is_staff: redirect_url = "/hidden-core-database/"
            elif user.role == Role.CUSTOMER: redirect_url = "/profile/"
            
            return JsonResponse({"success": True, "redirect": redirect_url})

        return JsonResponse({
            "success": False, 
            "message": "Email/Username yoki parol noto'g'ri."
        }, status=400)


class RegisterView(View):
    """
    Handles 3-step registration matching `register_erp.html`.
    """
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
            
            return JsonResponse({"success": True, "redirect": redirect_url})

        except DomainError as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": "Kutilmagan xatolik yuz berdi."}, status=500)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")
