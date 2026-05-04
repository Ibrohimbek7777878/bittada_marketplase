"""Celery tasks for `auth_methods` — out-of-band delivery of OTPs."""
from __future__ import annotations

import logging

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger("bittada.auth")


@shared_task(name="auth.send_otp_email")
def send_otp_email(target: str, code: str) -> None:
    """Email an OTP. In dev this prints to console (see EMAIL_BACKEND)."""
    send_mail(
        subject="Bittada — verification code",
        message=f"Your code is: {code}\nValid for 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[target],
        fail_silently=False,
    )


@shared_task(name="auth.send_otp_sms")
def send_otp_sms(target: str, code: str) -> None:
    """Send an SMS OTP via the configured provider (Eskiz, etc.)."""
    # TODO(integrations.sms): wire the configured provider; log-only for now.
    logger.info("sms_otp_dispatch", extra={"target": target, "code_len": len(code)})


@shared_task(name="auth.cleanup_expired_otps")
def cleanup_expired_otps() -> int:
    """Daily — drop OTPs older than 24h to keep the table small."""
    from datetime import timedelta

    from django.utils import timezone

    from .models import OtpCode

    cutoff = timezone.now() - timedelta(hours=24)
    deleted, _ = OtpCode.objects.filter(created_at__lt=cutoff).delete()
    return int(deleted)
