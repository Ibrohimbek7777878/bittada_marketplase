from django.urls import path, include # URL yo'llari
from rest_framework.routers import DefaultRouter # DRF Router
from .views import PageContentViewSet # ViewSetni import qilish

app_name = "pages" # App nomi

router = DefaultRouter() # Router obyektini yaratish
router.register("content", PageContentViewSet, basename="content") # ViewSetni ro'yxatdan o'tkazish

urlpatterns = [
    path("", include(router.urls)), # Router yo'llarini qo'shish
]
