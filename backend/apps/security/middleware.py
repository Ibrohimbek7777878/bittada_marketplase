"""
Request middleware.

  * `IPBlockMiddleware` — blocks requests from banned IPs early in the stack.
  * `RequestContextMiddleware` — stores ip + user agent on `request.bittada`
    so deeper layers (services, audit) can read them without coupling to HTTP.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone

from core.utils import client_ip, user_agent

from .models import IpBlock


@dataclass(slots=True)
class RequestContext:
    ip: str | None
    user_agent: str
    started_at: float


class IPBlockMiddleware:
    """Reject requests from active IP blocks before any view runs."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        ip = client_ip(request)
        if ip and self._is_blocked(ip):
            return JsonResponse(
                {"error": {"code": "ip_blocked", "message": "Your IP is blocked."}},
                status=403,
            )
        return self.get_response(request)

    @staticmethod
    def _is_blocked(ip: str) -> bool:
        now = timezone.now()
        return IpBlock.objects.filter(ip=ip).filter(
            models_q(until__isnull=True) | models_q(until__gt=now)
        ).exists()


class RequestContextMiddleware:
    """Attach a small context object so the rest of the stack can read it."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        import time
        request.bittada = RequestContext(  # type: ignore[attr-defined]
            ip=client_ip(request),
            user_agent=user_agent(request),
            started_at=time.monotonic(),
        )
        return self.get_response(request)


# Local helper to avoid an extra `from django.db.models import Q` everywhere.
def models_q(**kwargs):  # type: ignore[no-untyped-def]
    from django.db.models import Q
    return Q(**kwargs)
