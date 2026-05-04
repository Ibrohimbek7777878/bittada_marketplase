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
from .models import Service, Booking, BookingStatus
from .selectors import check_service_availability, get_service_next_slot


def create_booking(*, service_id: int, customer, notes: str = "") -> Booking:
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

        booking = Booking.objects.create(
            service=service,
            customer=customer,
            status=BookingStatus.QUEUE,
            notes=notes,
        )
    return booking


def advance_booking_status(*, booking_id: int, actor) -> Booking:
    """
    Buyurtma statusini keyingi bosqichga o'tkazish.
    Faqat xizmat egasi yoki admin bajarishi mumkin.
    """
    order = [
        BookingStatus.QUEUE,
        BookingStatus.SCHEDULED,
        BookingStatus.IN_PROGRESS,
        BookingStatus.COMPLETED,
    ]
    with transaction.atomic():
        booking = Booking.objects.select_for_update().get(id=booking_id)

        # Permission check: owner or admin
        if booking.service.user != actor and not actor.is_staff:
            raise ValueError("Ruxsat yo'q")

        current_index = order.index(booking.status)
        if current_index < len(order) - 1:
            booking.status = order[current_index + 1]
            booking.save(update_fields=["status", "updated_at"])

    return booking


def add_progress_update(*, booking_id: int, actor, text: str, photo_url: str = "") -> Booking:
    """
    Jonli progress oqimiga yangilanish qo'shish.
    """
    from django.utils import timezone

    with transaction.atomic():
        booking = Booking.objects.select_for_update().get(id=booking_id)

        if booking.service.user != actor and not actor.is_staff:
            raise ValueError("Ruxsat yo'q")

        feed = booking.progress_feed or []
        feed.append({
            "time": timezone.now().strftime("%d.%m.%Y %H:%M"),
            "text": text,
            "photo_url": photo_url,
        })
        booking.progress_feed = feed
        booking.save(update_fields=["progress_feed", "updated_at"])

    return booking
