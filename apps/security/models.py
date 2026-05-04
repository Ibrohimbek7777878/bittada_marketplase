"""
Security primitives.

  * `IpBlock` — explicit, time-bounded IP bans.
  * `AuditLog` — immutable record of sensitive actions for compliance.
  * `RequestLog` — lightweight per-request fingerprint for forensics
    (keep a short retention; rotate weekly).
"""
from __future__ import annotations

from django.db import models
from django.utils import timezone

from core.models import BaseModel


class IpBlock(BaseModel):
    """Block list. `until=NULL` means permanent."""

    ip = models.GenericIPAddressField(db_index=True)
    reason = models.CharField(max_length=200)
    until = models.DateTimeField(null=True, blank=True, db_index=True)
    created_by = models.ForeignKey(
        "users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )

    class Meta:
        db_table = "security_ip_block"
        indexes = [models.Index(fields=["ip", "until"])]

    def is_active(self) -> bool:
        return self.until is None or self.until > timezone.now()


class AuditLog(BaseModel):
    """
    Append-only audit trail.

    Use this for:
      * admin actions (role changes, manual unlocks, refunds)
      * financial events (escrow release, withdrawal)
      * permission grants
    """

    actor = models.ForeignKey(
        "users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )
    action = models.CharField(max_length=120, db_index=True)
    target_type = models.CharField(max_length=80, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "security_audit_log"
        indexes = [
            models.Index(fields=["actor", "created_at"]),
            models.Index(fields=["target_type", "target_id"]),
        ]


class RequestLog(BaseModel):
    """Lightweight forensic record. Truncate older rows aggressively."""

    method = models.CharField(max_length=8)
    path = models.CharField(max_length=400)
    status_code = models.PositiveSmallIntegerField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(
        "users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )
    user_agent = models.CharField(max_length=512, blank=True)
    duration_ms = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "security_request_log"
        indexes = [
            models.Index(fields=["ip", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]
