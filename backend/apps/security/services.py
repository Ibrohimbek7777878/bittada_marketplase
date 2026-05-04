"""Security services — auditing, blocking, lockout handling."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.utils import timezone

from .models import AuditLog, IpBlock


def record_audit(
    *,
    actor: Any | None,
    action: str,
    target_type: str = "",
    target_id: str | int | None = None,
    payload: dict[str, Any] | None = None,
    ip: str | None = None,
    ua: str = "",
) -> AuditLog:
    """One-line helper used everywhere a sensitive event happens."""
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else "",
        payload=payload or {},
        ip=ip,
        user_agent=ua,
    )


def block_ip(*, ip: str, reason: str, hours: int | None = None, actor=None) -> IpBlock:  # type: ignore[no-untyped-def]
    until = timezone.now() + timedelta(hours=hours) if hours else None
    return IpBlock.objects.create(ip=ip, reason=reason, until=until, created_by=actor)


def on_axes_lockout(request, credentials):  # type: ignore[no-untyped-def]
    """
    django-axes lockout callback.

    Wired in `settings.AXES_LOCKOUT_CALLABLE`. Records an audit log and (after
    repeated lockouts) escalates to a temporary IP block.
    """
    from django.http import JsonResponse

    ip = getattr(getattr(request, "bittada", None), "ip", None) or request.META.get("REMOTE_ADDR")
    record_audit(
        actor=None,
        action="auth.lockout",
        ip=ip,
        ua=getattr(getattr(request, "bittada", None), "user_agent", ""),
        payload={"username": credentials.get("username") if credentials else None},
    )

    recent = AuditLog.objects.filter(
        action="auth.lockout",
        ip=ip,
        created_at__gte=timezone.now() - timedelta(hours=24),
    ).count()
    if ip and recent >= 3:
        block_ip(ip=ip, reason="Repeated auth lockouts", hours=6)

    return JsonResponse(
        {"error": {"code": "locked", "message": "Too many failed attempts. Try later."}},
        status=429,
    )
