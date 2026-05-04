# i18n Utility Yangilanishi hujjatnomasi

## Muammo
Tarjimalar va matnlar faqat `i18n.js` fayli ichida statik holda saqlanar edi. Ularni dinamik o'zgartirish uchun kodni qayta yozish talab qilinar edi.

## Yechim
1.  `initI18n` funksiyasi yangilandi: endi u birinchi navbatda backenddan (API orqali) tarjimalarni yuklab olishga harakat qiladi.
2.  `loadRemoteTranslations` funksiyasi qo'shildi: u `/api/v1/pages/content/all/{lang}/` endpointidan ma'lumotlarni tortadi.
3.  Agarda backenddan ma'lumot kelmasa yoki xatolik bo'lsa, tizim avtomatik ravishda statik (fayl ichidagi) tarjimalarga o'tadi (fallback).
4.  Kod qatorlariga batafsil kommentariyalar qo'shildi.

## O'zgartirilgan fayllar
- `frontend_new/src/utils/i18n.js`: Dinamik yuklash mantig'i qo'shildi.

## Ta'sir
Endi saytdagi barcha yozuvlar admin tomonidan o'zgartirilishi bilanoq saytda aks etadi.
