# User Model Phone Update

## Muammo
Mavjud `User` modelida faqat `email` orqali ro'yxatdan o'tish imkoniyati bor edi. Foydalanuvchilar telefon raqami orqali ham ro'yxatdan o'tishlari uchun bazada telefon raqami saqlanadigan maydon mavjud emas edi.

## Yechim
1.  `apps.users.models.User` modeliga `phone` maydoni qo'shildi.
2.  `phone` maydoni `unique=True` qilib belgilandi, ya'ni bir xil raqam bilan ikki marta ro'yxatdan o'tib bo'lmaydi.
3.  `UserManager` klasidagi `_create` funksiyasi telefon raqami bilan ishlashga moslashtirildi.
4.  Telefon raqami uchun validatsiya (RegexValidator) qo'shildi.

## O'zgartirilgan fayllar
- `backend/apps/users/models.py`: Modelga `phone` maydoni va validatori qo'shildi.

## Ta'sir
Ushbu o'zgarish mavjud email orqali kirish tizimiga zarar yetkazmaydi, chunki `phone` maydoni ixtiyoriy (`null=True, blank=True`) qilib qoldirildi. Kelajakda telefon orqali OTP (SMS) yuborish tizimi uchun zamin yaratadi.
