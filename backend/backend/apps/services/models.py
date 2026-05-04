from django.db import models
from apps.users.models import User # Foydalanuvchi modeli bilan bog'lash uchun

class Service(models.Model): # Xizmat ko'rsatuvchi usta/mutaxassis modeli
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='specialist_services', null=True, blank=True) # Foydalanuvchi akkaunti
    name = models.CharField(max_length=255) # Mutaxassis ismi
    specialty = models.CharField(max_length=255) # Mutaxassislik sohasi (Dizayner, usta va h.k.)
    rating = models.FloatField(default=0.0) # Reyting (0 dan 5 gacha)
    review_count = models.IntegerField(default=0) # Sharhlar soni
    location = models.CharField(max_length=255, default="Toshkent") # Manzil
    experience = models.IntegerField(default=0) # Ish tajribasi (yil)
    projects_completed = models.IntegerField(default=0) # Yakunlangan loyihalar soni
    starting_price = models.DecimalField(max_digits=12, decimal_places=2) # Boshlang'ich xizmat narxi
    is_available = models.BooleanField(default=True) # Ustaning hozirda bo'shligi
    category = models.CharField(max_length=100, default="Barchasi") # Toifa (Filtr uchun)
    
    created_at = models.DateTimeField(auto_now_add=True) # Yaratilgan vaqti
    updated_at = models.DateTimeField(auto_now=True) # Yangilangan vaqti

    def __str__(self): # Modelning matnli ko'rinishi
        return f"{self.name} - {self.specialty}" # Ism va soha ko'rinishida

    class Meta: # Model sozlamalari
        verbose_name = "Xizmat/Usta" # Yagona nom
        verbose_name_plural = "Xizmatlar va Ustalar" # Ko'plik nomi


class BookingStatus(models.TextChoices):
    QUEUE = "queue", "Navbatda"
    SCHEDULED = "scheduled", "Rejalashtirilgan"
    IN_PROGRESS = "in_progress", "Jarayonda"
    COMPLETED = "completed", "Yakunlangan"
    CANCELLED = "cancelled", "Bekor qilingan"


class Booking(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_bookings')
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.QUEUE)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Progress Feed (JSON or separate model, using TextField for now)
    progress_feed = models.JSONField(default=list, blank=True) # Stores [{time, text, photo_url}, ...]
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.service.name} by {self.customer.username}"
