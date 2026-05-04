from django.contrib import admin
from .models import Service

@admin.register(Service) # Modelni admin panelda ro'yxatdan o'tkazish
class ServiceAdmin(admin.ModelAdmin): # Admin panel sozlamalari
    list_display = ("name", "specialty", "category", "rating", "is_available") # Ko'rinadigan ustunlar
    list_filter = ("category", "is_available", "location") # Filtrlash opsiyalari
    search_fields = ("name", "specialty") # Qidiruv maydonlari
