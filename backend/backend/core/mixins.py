"""Reusable view / serializer mixins."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response


class AuditedCreateMixin:
    """ViewSet mixin that records `created_by` from the request user on POST."""

    def perform_create(self, serializer):  # type: ignore[no-untyped-def]
        serializer.save(created_by=self.request.user)


class AuditedUpdateMixin:
    def perform_update(self, serializer):  # type: ignore[no-untyped-def]
        serializer.save(updated_by=self.request.user)


class StandardOkResponseMixin:
    """Helper for ad-hoc actions returning `{ok: true}`."""

    def ok(self, data: Any = None) -> Response:  # type: ignore[override]
        body = {"ok": True}
        if data is not None:
            body["data"] = data
        return Response(body, status=status.HTTP_200_OK)
