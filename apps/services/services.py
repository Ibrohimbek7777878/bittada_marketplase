"""
Business logic for `services`.

Functions in this module mutate state. They should:
- accept primitive args + the actor user;
- run inside a transaction when touching multiple rows;
- raise ValueError on rule violations (DomainError placeholder);
- emit notifications/Celery tasks rather than inline I/O.
"""
from __future__ import annotations
from django.db import transaction
from .models import Service, ServiceBooking, ServiceBookingStatus
from .selectors import check_service_availability, get_service_next_slot


def create_booking(*, service_id: int, customer, notes: str = "") -> ServiceBooking:
    """
    Yangi bron yaratish — double-booking oldini oladi.
    select_for_update() orqali race condition bloklanadi.
    """
    with transaction.atomic():
        # Row-level lock on the service to prevent concurrent double-booking
        service = Service.objects.select_for_update().get(id=service_id)

        if not check_service_availability(service_id):
            next_slot = get_service_next_slot(service_id)
            raise ValueError(
                f"Usta hozirda band. Keyingi bo'sh vaqt: {next_slot}"
            )

        booking = ServiceBooking.objects.create(
            service=service,
            customer=customer,
            status=ServiceBookingStatus.INQUIRY,
            description=notes,
        )
    return booking


def advance_booking_status(*, booking_id: int, actor) -> ServiceBooking:
    """
    Buyurtma statusini keyingi bosqichga o'tkazish.
    Faqat xizmat egasi yoki admin bajarishi mumkin.
    """
    order = [
        ServiceBookingStatus.INQUIRY,
        ServiceBookingStatus.QUEUE,
        ServiceBookingStatus.SCHEDULED,
        ServiceBookingStatus.IN_PROGRESS,
        ServiceBookingStatus.COMPLETED,
    ]
    with transaction.atomic():
        booking = ServiceBooking.objects.select_for_update().get(id=booking_id)

        # Permission check: owner or admin
        if booking.service.provider != actor and not actor.is_staff:
            raise ValueError("Ruxsat yo'q")

        current_index = order.index(booking.status)
        if current_index < len(order) - 1:
            booking.status = order[current_index + 1]
            booking.save(update_fields=["status", "updated_at"])

    return booking


def add_progress_update(*, booking_id: int, actor, text: str, photo_url: str = "") -> ServiceBooking:
    """
    Jonli progress oqimiga yangilanish qo'shish (TZ §11).
    """
    from django.utils import timezone

    with transaction.atomic():
        booking = ServiceBooking.objects.select_for_update().get(id=booking_id)

        if booking.service.provider != actor and not actor.is_staff:
            raise ValueError("Ruxsat yo'q")

        # Update last progress fields
        booking.last_progress_update = timezone.now()
        booking.last_progress_text = text
        if photo_url:
            # Save photo URL - in production this would be an ImageField upload
            booking.last_progress_photo = photo_url
        booking.save(update_fields=["last_progress_update", "last_progress_text", "last_progress_photo", "updated_at"])

        # Also create a ServiceProgressUpdate record for full history
        from .models import ServiceProgressUpdate
        ServiceProgressUpdate.objects.create(
            booking=booking,
            provider=actor,
            text=text,
            location=booking.address[:100] if booking.address else "",
        )

    return booking
