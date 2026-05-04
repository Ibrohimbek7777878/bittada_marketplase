# Config URLs Yangilanishi hujjatnomasi

## Muammo
`config/urls.py` faylida `apps.pages.urls` ikki marta (ham API v1 ichida, ham asosiy urlpatterns ichida) ro'yxatdan o'tkazilgan edi. Bu chalkashlikka olib kelishi mumkin edi.

## Yechim
1.  Asosiy `urlpatterns` ichidagi ortiqcha `pages/` yo'li olib tashlandi.
2.  Barcha sahifa kontentiga oid so'rovlar endi faqat `/api/v1/pages/` orqali amalga oshirilishi ta'minlandi.
3.  Kod qatorlariga batafsil kommentariyalar qo'shildi.

## O'zgartirilgan fayllar
- `backend/config/urls.py`: Ortiqcha URLlar tozalandi.

## Ta'sir
URLlar strukturasi tozalab olindi va standartga keltirildi.
