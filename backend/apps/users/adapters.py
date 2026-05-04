from __future__ import annotations

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.urls import reverse
from apps.users.models import Role

class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_authenticated:
            if user.role == Role.CUSTOMER:
                return "/profile/"
            elif user.is_staff:
                return "/hidden-core-database/"
        return super().get_login_redirect_url(request)

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        return "/profile/"
