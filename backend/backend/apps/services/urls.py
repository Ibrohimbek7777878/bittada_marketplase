from django.urls import path
from .views import (
    services_view, service_type_detail,
    create_booking, booking_dashboard,
    advance_booking, post_progress,
)

app_name = "services"

urlpatterns: list = [
    path("", services_view, name="services"),
    path("my-bookings/", booking_dashboard, name="booking_dashboard"),
    path("book/<int:service_id>/", create_booking, name="create_booking"),
    path("booking/<int:booking_id>/advance/", advance_booking, name="advance_booking"),
    path("booking/<int:booking_id>/progress/", post_progress, name="post_progress"),
    path("<slug:service_slug>/", service_type_detail, name="service_type_detail"),
]
