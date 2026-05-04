"""URL routes for `api`. Mounted under `/api/v1/api/`."""
from __future__ import annotations

from django.urls import path

from .views import api_test_connection, system_health_view
from .csrf_views import get_csrf_token

app_name = "api"

urlpatterns: list = [
    path("test-connection/", api_test_connection, name="test-connection"),
    path("csrf-token/", get_csrf_token, name="csrf-token"),
    path("system/health/", system_health_view, name="system-health"),
]
