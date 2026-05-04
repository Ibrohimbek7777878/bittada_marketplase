# CustomerSignupForm (auth_methods/forms.py)

## Umumiy ma'lumot
Yangi fayl: `backend/apps/auth_methods/forms.py`. Mijozlar uchun soddalashtirilgan ro'yxatdan o'tish formasi.

## Qanday muammoni hal qiladi?
Mavjud tizimda ro'yxatdan o'tishda ko'p maydonlar (email, username, role, account_type, professions, invite_code) bor, bu mijozlar uchun qo'noq. Mijozlar faqat ism va telefon raqami bilan tez ro'yxatdan o'tishni xohlaydi. Shuningdek, ularning username avtomatik ravishda telefon raqami bilan bir xil bo'lishi kerak.

## Qanday o'zgarish kiritildi?
1. **CustomerSignupForm** yaratildi - `forms.Form` asosida.
2. Majburiy maydonlar: `first_name`, `phone_number`, `password`, `password_confirm`.
3. `phone_number` maydoni +998XXXXXXXXX formatida tekshiriladi (PHONE_VALIDATOR).
4. `clean_phone_number()` metodi telefonni tozalaydi va bandligini tekshiradi.
5. `clean()` metodi parolni tesdiqlashni tekshiradi.
6. `save()` metodi:
   - Username ni telefon raqamidan yaratadi (`slugify` orqali).
   - `User.objects.create_user()` orqali foydalanuvchi yaratadi.
   - Rol `Role.CUSTOMER` sifatida belgilanadi.
   - `is_staff=False`, `is_superuser=False` (create_user da sukut bo'yicha).
   - Email `None` qo'yiladi (mijozda emal majburiy emas).

## Muhim jihatlar
- Username avtomatik generatsiya qilinadi (telefon + qo'shimcha).
- `is_staff` va `is_superuser` har doim False bo'lib, admin panelga kirishni cheklaydi.
- Formadan o'tgach, foydalanuvchi darhol tizimga kiritiladi (login) va profil sahifasiga yo'naltiriladi (view da).
- Xavfsizlik: telefon bandligi tekshiriladi, parol min 6 ta belgi.