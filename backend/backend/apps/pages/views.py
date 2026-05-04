from rest_framework import viewsets, permissions # Viewsets va huquqlar
from rest_framework.response import Response # Javob qaytarish
from rest_framework.decorators import action # Qo'shimcha amallar
from .models import PageContent # Model
from .serializers import PageContentSerializer # Serializer

from rest_framework import viewsets, permissions, status # Viewsets va status kodlari
from rest_framework.response import Response # Javob qaytarish
from rest_framework.decorators import action # Dekoratordar
from .models import PageContent # Model
from .serializers import PageContentSerializer # Serializer

class PageContentViewSet(viewsets.ModelViewSet): # Sahifa matnlarini boshqarish klassi
    queryset = PageContent.objects.all() # Barcha obyektlarni qidirish
    serializer_class = PageContentSerializer # Serializerni sozlash
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # O'qish ochiq, yozish faqat auth uchun

    def create(self, request, *args, **kwargs): # Yangi matn yaratish yoki mavjudini yangilash
        """
        Agar key va language mavjud bo'lsa yangilaydi, bo'lmasa yaratadi.
        Bu admin panelda saqlash tugmasi bir xil ishlashi uchun kerak.
        """
        key = request.data.get('key') # Kalitni olish
        language = request.data.get('language', 'uz') # Tilni olish (yoki 'uz')
        value = request.data.get('value') # Yangi matnni olish
        
        # update_or_create mantiqi: bazadan qidirish va o'zgartirish
        obj, created = PageContent.objects.update_or_create(
            key=key, 
            language=language,
            defaults={'value': value} # Faqat 'value' o'zgaradi
        )
        
        serializer = self.get_serializer(obj) # Obyektni JSONga o'girish
        return Response(serializer.data, status=status.HTTP_200_OK) # Javob qaytarish

    @action(detail=False, methods=['get'], url_path='all/(?P<lang>\w+)') # Til bo'yicha hammasini olish
    def get_all_by_lang(self, request, lang=None): # Funksiya
        """Barcha matnlarni lug'at ko'rinishida qaytaradi."""
        contents = PageContent.objects.filter(language=lang) # Til bo'yicha filter
        data = {item.key: item.value for item in contents} # {key: value} formatida yig'ish
        return Response(data) # JSON javob qaytarish
