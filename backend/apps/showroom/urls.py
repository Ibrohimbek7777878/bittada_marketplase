"""URL routes for `showroom` — Django Templates."""
from __future__ import annotations

from django.urls import path
from .views import showroom_view

urlpatterns: list = [
    path("", showroom_view, name="showroom"),
]
