from django.contrib import admin # Admin panel kutubxonasi
from .models import PageContent # Modelni import qilish

@admin.register(PageContent) # Modelni admin panelga ro'yxatdan o'tkazish
class PageContentAdmin(admin.ModelAdmin): # Admin sozlamalari
    list_display = ("key", "language", "value", "updated_at") # Ro'yxatda ko'rinadigan ustunlar
    list_filter = ("language",) # Filtrlash (til bo'yicha)
    search_fields = ("key", "value") # Qidirish imkoniyati (kalit va matn bo'yicha)
    ordering = ("key",) # Saralash (kalit bo'yicha)
