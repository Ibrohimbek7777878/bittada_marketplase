from django.db import models # Django modellarini import qilish
from core.models import BaseModel # Asosiy modelni core papkasidan import qilish

class PageContent(BaseModel): # Sayt kontenti uchun model
    """
    Dinamik kontent (matnlar, yozuvlar) uchun model.
    Har bir yozuv unikal 'key' orqali aniqlanadi.
    """
    
    key = models.CharField( # Kalit maydoni (masalan: 'home_title')
        max_length=255, # Maksimal uzunlik
        db_index=True, # Tez qidirish uchun indeks
        help_text="Kontent identifikatori (masalan: nav_home)" # Yordamchi matn
    )
    value = models.TextField( # Qiymat maydoni (asl matn)
        help_text="Ko'rinadigan matn yoki yozuv" # Yordamchi matn
    )
    language = models.CharField( # Til maydoni
        max_length=10, # Uzunlik (uz, ru, en)
        default='uz', # Sukut bo'yicha o'zbekcha
        choices=[('uz', 'Uzbek'), ('ru', 'Russian'), ('en', 'English')] # Tanlovlar
    )

    class Meta: # Model sozlamalari
        db_table = "pages_content" # Ma'lumotlar bazasidagi jadval nomi
        unique_together = ("key", "language") # Kalit va til kombinatsiyasi unikal bo'lishi shart
        verbose_name = "Sahifa kontenti" # Admin panelda ko'rinadigan nomi
        verbose_name_plural = "Sahifa kontentlari" # Ko'plikdagi nomi

    def __str__(self): # Obyektni matn ko'rinishida qaytarish
        return f"{self.key} [{self.language}]" # Kalit va tilni ko'rsatish
