"""
TZ §11 - Services domain.
Booking-style listing with availability calendar and progress feed.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class ServiceCategory(models.TextChoices):
    """TZ §11 - Xizmat kategoriyalari"""
    DESIGN = "design", "Dizayn"
    INSTALLATION = "installation", "O'rnatish/Montaj"
    REPAIR = "repair", "Ta'mirlash"
    UPHOLSTERY = "upholstery", "Perig'iv/tikish"
    ASSEMBLY = "assembly", "Yig'ish"
    DELIVERY = "delivery", "Yetkazib berish"
    OTHER = "other", "Boshqa"


class Service(BaseModel):
    """
    TZ §11 - Xizmat ko'rsatuvchi mutaxassis.
    Provider availability calendar visible to public.
    """
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='services',
        limit_choices_to={"role__in": ["seller", "internal_supplier"]},
        verbose_name=_("Mutaxassis"),
        null=True,
        blank=True
    )
    title = models.CharField(
        max_length=255,
        default="Xizmat",
        verbose_name=_("Sarlavha")
    )
    category = models.CharField(
        max_length=20,
        choices=ServiceCategory.choices,
        default=ServiceCategory.OTHER,
        verbose_name=_("Kategoriya")
    )
    description = models.TextField(
        verbose_name=_("Tavsif"),
        null=True,
        blank=True
    )

    # Pricing
    price_type = models.CharField(
        max_length=20,
        choices=[
            ("fixed", "Fixed price"),
            ("hourly", "Per hour"),
            ("scope", "Scope-based"),
            ("negotiable", "Negotiable"),
        ],
        default="fixed",
        verbose_name=_("Narx turi")
    )
    starting_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Boshlang'ich narx")
    )

    # Availability - visible to public
    is_open_for_booking = models.BooleanField(
        default=True,
        verbose_name=_("Yangi buyurtma qabul qilyapti?")
    )
    currently_working = models.BooleanField(
        default=False,
        verbose_name=_("Hozirda ishlamoqda?")
    )
    currently_at_location = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Hozirgi joylashuv")
    )

    # Stats
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        verbose_name=_("Reyting")
    )
    review_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sharhlar soni")
    )
    projects_completed = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Yakunlangan loyihalar")
    )

    # Working hours (JSON)
    working_hours = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Ish soatlari"),
        help_text=_('{"mon": {"open": "09:00", "close": "18:00"}, ...}')
    )

    class Meta:
        verbose_name = "Xizmat"
        verbose_name_plural = "Xizmatlar"
        ordering = ["-rating", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} - {self.provider.username}"


class ServiceBookingStatus(models.TextChoices):
    """TZ §11 - Booking status timeline"""
    INQUIRY = "inquiry", "So'rov"
    QUEUE = "queue", "Navbatda"
    SCHEDULED = "scheduled", "Rejalashtirilgan"
    IN_PROGRESS = "in_progress", "Jarayonda"
    COMPLETED = "completed", "Yakunlandi"
    CANCELLED = "cancelled", "Bekor qilindi"
    DISPUTED = "disputed", "Nizo"


class ServiceBooking(BaseModel):
    """
    TZ §11 - Service booking with timeline.
    Escrow payment + progress feed.
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_("Xizmat")
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='service_bookings',
        verbose_name=_("Mijoz")
    )
    status = models.CharField(
        max_length=20,
        choices=ServiceBookingStatus.choices,
        default=ServiceBookingStatus.INQUIRY,
        verbose_name=_("Holat")
    )

    # Scheduling
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Rejalashtirilgan sana")
    )
    scheduled_time_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Boshlanish vaqti")
    )
    scheduled_time_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Tugash vaqti")
    )

    # Details
    description = models.TextField(
        verbose_name=_("Ish tavsifi"),
        null=True,
        blank=True
    )
    address = models.TextField(
        verbose_name=_("Manzil"),
        null=True,
        blank=True
    )
    agreed_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Kelishilgan narx")
    )

    # Escrow reference
    escrow = models.OneToOneField(
        "escrow.Escrow",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_booking',
        verbose_name=_("Escrow")
    )

    # Progress feed (TZ §11)
    # Updated by provider: "Currently working at: location"
    last_progress_update = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Oxirgi progress yangilanishi")
    )
    last_progress_text = models.TextField(
        blank=True,
        verbose_name=_("Oxirgi progress matni")
    )
    last_progress_photo = models.ImageField(
        upload_to="services/progress/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("Oxirgi progress rasmi")
    )

    # Completion
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Yakunlangan vaqti")
    )
    customer_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Mijoz bahosi")
    )
    customer_review = models.TextField(
        blank=True,
        verbose_name=_("Mijoz sharhi")
    )

    class Meta:
        verbose_name = "Xizmat buyurtmasi"
        verbose_name_plural = "Xizmat buyurtmalari"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Booking #{self.id} - {self.service.title}"


class ServiceProgressUpdate(BaseModel):
    """
    TZ §11 - Live progress feed.
    Provider can post updates with photos.
    """
    booking = models.ForeignKey(
        ServiceBooking,
        on_delete=models.CASCADE,
        related_name='progress_updates',
        verbose_name=_("Buyurtma")
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress_updates',
        verbose_name=_("Mutaxassis")
    )

    text = models.TextField(
        verbose_name=_("Yangilanish matni")
    )
    photo = models.ImageField(
        upload_to="services/progress/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("Rasm")
    )
    location = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Joylashuv")
    )

    # Status change
    new_status = models.CharField(
        max_length=20,
        choices=ServiceBookingStatus.choices,
        null=True,
        blank=True,
        verbose_name=_("Yangi status (agar o'zgargan bo'lsa)")
    )

    class Meta:
        verbose_name = "Progress yangilanishi"
        verbose_name_plural = "Progress yangilanishlari"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Update on Booking #{self.booking_id}"


class ProviderAvailability(BaseModel):
    """
    TZ §11 - Provider availability slots.
    Public calendar for booking.
    """
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availability_slots',
        verbose_name=_("Mutaxassis")
    )
    date = models.DateField(
        verbose_name=_("Sana")
    )
    time_start = models.TimeField(
        verbose_name=_("Boshlanish")
    )
    time_end = models.TimeField(
        verbose_name=_("Tugash")
    )
    is_booked = models.BooleanField(
        default=False,
        verbose_name=_("Bandmi?")
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name=_("Bloklangan?")
    )

    class Meta:
        verbose_name = "Bandlik vaqti"
        verbose_name_plural = "Bandlik vaqtlari"
        unique_together = ["provider", "date", "time_start"]
        ordering = ["date", "time_start"]

    def __str__(self) -> str:
        return f"{self.provider.username} @ {self.date} {self.time_start}-{self.time_end}"
