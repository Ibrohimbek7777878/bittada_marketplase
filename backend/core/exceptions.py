"""
Domain exceptions and a unified DRF exception handler.

We surface a stable error envelope so frontend / mobile can render messages
without parsing different shapes per endpoint.
"""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler


class DomainError(Exception):
    """Raised by services when a business rule is violated."""

    code: str = "domain_error"
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code:
            self.code = code


class PermissionDeniedDomain(DomainError):
    code = "permission_denied"
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundDomain(DomainError):
    code = "not_found"
    status_code = status.HTTP_404_NOT_FOUND


class ConflictDomain(DomainError):
    code = "conflict"
    status_code = status.HTTP_409_CONFLICT


class RateLimitedDomain(DomainError):
    code = "rate_limited"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Map DomainError + DRF exceptions to a stable JSON envelope."""
    if isinstance(exc, DomainError):
        return Response(
            {"error": {"code": exc.code, "message": exc.message}},
            status=exc.status_code,
        )

    response = drf_default_handler(exc, context)
    if response is None:
        return None

    detail = response.data
    if isinstance(detail, dict) and "detail" in detail:
        message = str(detail["detail"])
        code = getattr(detail["detail"], "code", "error")
    else:
        message = "Validation error"
        code = "validation_error"

    response.data = {
        "error": {
            "code": code,
            "message": message,
            "fields": detail if isinstance(detail, dict) and "detail" not in detail else None,
        }
    }
    return response
