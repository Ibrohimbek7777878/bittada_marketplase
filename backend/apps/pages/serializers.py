from rest_framework import serializers # Serializerlar kutubxonasi
from .models import PageContent # Modelni import qilish

class PageContentSerializer(serializers.ModelSerializer): # PageContent uchun serializer
    class Meta: # Meta sozlamalar
        model = PageContent # Modelni bog'lash
        fields = ['key', 'value', 'language'] # JSONda ko'rinadigan maydonlar
