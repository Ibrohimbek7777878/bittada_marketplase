"""URL routes for users & auth."""
from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MeViewSet, PublicProfileView, LoginView, RegisterView, LogoutView

app_name = "users"

router = DefaultRouter()
router.register("me", MeViewSet, basename="me")

urlpatterns = [
    # Auth (Template Views)
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
    # Profiles
    path("u/<str:username>/", PublicProfileView.as_view(), name="public-profile-api"),
    
    *router.urls,
]
