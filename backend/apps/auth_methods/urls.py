"""Auth routes — `/api/v1/auth/...`"""
from __future__ import annotations

from django.urls import path

from .views import OtpConfirmView, OtpRequestView, RegisterView, TokenRefresh, TokenView, SocialLoginView, TelegramCallbackView

app_name = "auth_methods"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenView.as_view(), name="login"),
    path("refresh/", TokenRefresh.as_view(), name="refresh"),
    path("otp/request/", OtpRequestView.as_view(), name="otp-request"),
    path("otp/confirm/", OtpConfirmView.as_view(), name="otp-confirm"),
    path("social-login/", SocialLoginView.as_view(), name="social-login"),
    path("telegram/callback/", TelegramCallbackView.as_view(), name="telegram-callback"),
    path("telegram/login/", TelegramCallbackView.as_view(), name="telegram-login-redirect"),
    path("telegram-callback/", TelegramCallbackView.as_view(), name="telegram-callback-root"),
]
