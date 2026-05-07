"""URL routes for `users`.

Two layers:

1. ``urlpatterns`` — DRF API mounted at ``/api/v1/users/``. JSON profile
   lookup and the authenticated-user ``/me/`` viewset live here.

2. ``public_template_urlpatterns`` — HTML routes mounted at site root via
   ``config/urls.py``. These give every registered user an Instagram-style
   public page at ``/@<username>/`` plus per-tab URLs and a dashboard
   profile editor at ``/dashboard/profile/edit/``.

Route names live in the global namespace (no ``users:`` prefix) so they
match how ``config/urls.py`` splats them into ``template_patterns``.
"""
from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from .role_register import RegisterPickerView, RoleRegisterView
from .views import (
    MeViewSet,
    PublicProfileView,
    UserProfileView,
)

app_name = "users"

router = DefaultRouter()
router.register("me", MeViewSet, basename="me")

# === DRF API (mounted at /api/v1/users/) ===
urlpatterns = [
    path("u/<str:username>/", PublicProfileView.as_view(), name="public-profile-api"),
    *router.urls,
]


# === HTML template routes (mounted at site root by config/urls.py) ===
public_template_urlpatterns = [
    # Instagram-style public profile + per-tab pages.
    path(
        "@<str:username>/",
        UserProfileView.as_view(),
        name="user_profile",
    ),
    path(
        "@<str:username>/products/",
        UserProfileView.as_view(),
        {"tab": "products"},
        name="user_profile_products",
    ),
    path(
        "@<str:username>/services/",
        UserProfileView.as_view(),
        {"tab": "services"},
        name="user_profile_services",
    ),
    path(
        "@<str:username>/portfolio/",
        UserProfileView.as_view(),
        {"tab": "portfolio"},
        name="user_profile_portfolio",
    ),
    path(
        "@<str:username>/contact/",
        UserProfileView.as_view(),
        {"tab": "contact"},
        name="user_profile_contact",
    ),
    # Role-based registration. ``/register/`` is the picker; per-role slugs
    # render the right form (``/register/master/``, ``.../designer/``, etc).
    path("register/role/", RegisterPickerView.as_view(), name="register_picker"),
    path(
        "register/role/<slug:role_slug>/",
        RoleRegisterView.as_view(),
        name="register_role",
    ),
    # NOTE: ``/dashboard/profile/edit/`` is wired in ``config/urls.py`` so it
    # sits BEFORE the management dashboard mount. See ``ProfileEditView``.
]
