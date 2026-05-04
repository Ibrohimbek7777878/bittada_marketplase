from django.contrib import admin
from .models import Service, ServiceBooking, ServiceProgressUpdate, ProviderAvailability


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "provider", "category", "rating", "is_open_for_booking", "starting_price")
    list_filter = ("category", "is_open_for_booking", "currently_working")
    search_fields = ("title", "description", "provider__username")
    raw_id_fields = ("provider",)


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ("id", "service", "customer", "status", "scheduled_date", "agreed_price")
    list_filter = ("status", "scheduled_date")
    search_fields = ("service__title", "customer__username", "description")
    raw_id_fields = ("service", "customer", "escrow")


@admin.register(ServiceProgressUpdate)
class ServiceProgressUpdateAdmin(admin.ModelAdmin):
    list_display = ("booking", "provider", "created_at", "new_status")
    list_filter = ("new_status", "created_at")
    search_fields = ("text", "location")
    raw_id_fields = ("booking", "provider")


@admin.register(ProviderAvailability)
class ProviderAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("provider", "date", "time_start", "time_end", "is_booked", "is_blocked")
    list_filter = ("is_booked", "is_blocked", "date")
    search_fields = ("provider__username",)
    raw_id_fields = ("provider",)
