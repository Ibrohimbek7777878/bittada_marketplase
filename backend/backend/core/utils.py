"""Common helpers — slug generation, IP extraction, etc."""
from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from slugify import slugify as _slugify


def slugify(value: str, *, max_length: int = 80) -> str:
    """Cyrillic-safe slug for usernames, categories, products."""
    return _slugify(value, max_length=max_length, lowercase=True, allow_unicode=False)


def client_ip(request: HttpRequest) -> str | None:
    """Best-effort client IP — trust X-Forwarded-For only behind a known proxy."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # The leftmost address is the original client.
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def user_agent(request: HttpRequest) -> str:
    return request.META.get("HTTP_USER_AGENT", "")[:512]


def deep_get(data: dict[str, Any], path: str, default: Any = None) -> Any:
    """`deep_get(d, "a.b.c")` → equivalent to chained .get with default."""
    cur: Any = data
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur
