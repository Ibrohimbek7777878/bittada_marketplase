"""URL routes for users — API and public seller profile."""
from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MeViewSet, PublicProfileView, UserProfileView, ProfileEditView

app_name = "users"

router = DefaultRouter()
router.register("me", MeViewSet, basename="me")

urlpatterns = [
    # API yo'nalishlari
    path("api/u/<str:username>/", PublicProfileView.as_view(), name="public-profile-api"),
    
    # HTML sahifalari
    path("u/@<str:username>/", UserProfileView.as_view(), name="user_profile"),
    path("u/<str:username>/", UserProfileView.as_view(), name="user_profile_legacy"),
    path("u/<str:username>/edit/", ProfileEditView.as_view(), name="profile_edit"),
    
    *router.urls,
]
