# Template: customer_profile.html

## Fayl: `backend/templates/customer_profile.html` (yangi)

## Maqsad
Mijoz (role='customer') uchun soddalashtirilgan profil sahifasi. Bu sahifada:
- Foydalanuvchining ismi va telefoni ko'rsatiladi.
- "Mening buyurtmalarim" bo'limi (hozircha bo'sh, keyin buyurtmalar ro'yxati bilan to'ldiriladi).
- "Profilni tahrirlash" tugmasi (profilni o'zgartirish sahifasiga yo'naltiradi).

## Xususiyar
- `base_erp.html` asosida; faqat asosiy ma'lumotlar va buyurtmalar bloki.
- Minimal interfeys: bitta kartada ma'lumotlar, biri buyurtmalar.
- "Profilni tahrirlash" tugmasi `profile_edit` URL ga (ya'ni `/profile/edit/`) yo'naltiradi. Bu esa `profile_erp.html` sahifasini ochadi (to'liq tahrirlash formasi).
- Mijozlar uchun maxsus; boshqa rollar (seller, admin) uchun `profile_erp.html` ishlatiladi (products/views.py profile_view da shart).

## O'xshashlik
`profile_erp.html` ga o'xshaydi, lekin sidebar, qo'shimcha menyular, qo'shimcha maydonlar yo'q.