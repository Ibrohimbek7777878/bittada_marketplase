"""URL routes for users — mounted at `/api/v1/users/`."""
from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MeViewSet, PublicProfileView
from apps.products.views import seller_profile_view # Template viewni import qilish

app_name = "users"

router = DefaultRouter()
router.register("me", MeViewSet, basename="me")

urlpatterns = [
    # API yo'nalishlari
    path("u/<str:username>/", PublicProfileView.as_view(), name="public-profile-api"),
    
    # Template yo'nalishi (TZ 7-band)
    path("u/<str:username>/template/", seller_profile_view, name="public-profile"),
    
    *router.urls,
]
