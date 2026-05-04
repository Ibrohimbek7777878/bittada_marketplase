# Auth-flow Serializerlar uchun o'zgarishlar hujjatnomasi

## Muammo
Ro'yxatdan o'tish jarayonida faqat `email` talab qilinardi. Foydalanuvchilar telefon raqami orqali ham ro'yxatdan o'tish imkoniyatiga ega bo'lishlari kerak.

## Yechim
1.  `RegisterSerializer` klassiga `phone` maydoni qo'shildi.
2.  `email` maydoni `required=False` qilindi, ya'ni foydalanuvchi yo email, yo telefon raqami bilan ro'yxatdan o'tishi mumkin.
3.  `validate` metodi orqali kamida bitta aloqa vositasi (email yoki telefon) borligi tekshirilishi ta'minlandi.
4.  Har bir qatorga batafsil tushuntirish kommentariyalari qo'shildi.

## O'zgartirilgan fayllar
- `backend/apps/auth_methods/serializers.py`: Serializerga `phone` maydoni va validatsiya mantiqi qo'shildi.

## Ta'sir
Mavjud email orqali ro'yxatdan o'tish tizimi saqlab qolindi, ammo endi tizim yanada kengayuvchan (extensible) bo'ldi.
