# Template: customer_register.html

## Fayl: `backend/templates/customer_register.html` (yangi)

## Maqsad
Mijozlar uchun soddalashtirilgan ro'yxatdan o'tish sahifasi. Faqat quyidagi maydonlarni talab qiladi:
- Ism (first_name)
- Telefon raqami (phone_number)
- Parol va parolni tasdiqlash

## Xususiyatlar
- `base_erp.html` asosida (bitta asosiy konteyner).
- Minimalistik dizayn: bir ustunli form, faqat majburiy maydonlar.
- JS orqali AJAX so'rov yuboriladi, xatolar real vaqtda ko'rsatiladi.
- Muvaffaqiyatli ro'yxatdan o'tgandan so'ng `profile/` sahifasiga yo'naltiriladi.

## Boshqa
- CSRF token qo'shilgan.
- Forma `CustomerSignupForm` (auth_methods/forms.py) orqali qabul qilinadi.
- `action` bo'sh (`""`), ya'ni joriy URL ga POST yuboriladi.
- JS fetch orqali POST qilinadi, redirect header bilan qaytariladi.