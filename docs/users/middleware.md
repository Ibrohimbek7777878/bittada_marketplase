# Customer Admin Blocker Middleware (users/middleware.py)

## Umumiy
Yangi fayl: `backend/apps/users/middleware.py`. Bu middleware mijozlar (role='customer') dan Django admin paneli (`/admin/` yoki `/hidden-core-database/`) ga kirishni cheklaydi.

## Muammo
Mijozlar ro'yxatdan o'tgach, ularning `is_staff=False`, lekin Django admin panelga kirishga urinib, 403 xatosini ko'rishi mumkin. Yoki ularni mansabizdan himoya qilish uchun qo'shimcha bloklagich kerak.

## Yechim
Middleware har bir so'rovda:
1. Foydalanuvchi autentifikatsiyalangan va `role='customer'` bo'lsa.
2. So'rov yo'li `/admin/` yoki `/hidden-core-database/` bilan boshlansa.
3. Ushbu so'rovni bloklaydi va foydalanuvchini `/profile/` sahifasiga qaytaradi (redirect).

Buning evaziga, mijozlar admin panaga har qanday urinishda avtomatik ravishda profilga qaytariladi.

## O'rnatish
`config/settings/base.py` da `MIDDLEWARE` ro'yxatiga qo'shildi:
```python
"apps.users.middleware.BlockCustomerAdminAccessMiddleware",
```
`AuthenticationMiddleware` dan keyin va `ManagementAccessMiddleware` dan keyin joylashdi.

## Qo'shimcha
Agar kerak bo'lsa, redirect o'rniga `HttpResponseForbidden` qaytarish mumkin (kodda comment sifatida qolgan).