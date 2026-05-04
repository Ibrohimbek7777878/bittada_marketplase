# Auth Serializers (auth_methods/serializers.py) — o'zgarishlar

## Umumiy
`BittadaTokenObtainPairSerializer` classida telefon raqami orqali autentifikatsiya qo'shildi.

## Muammo
Mijozlar faqat telefon raqami bilan ro'yxatdan o'tadi (email yo'q). Ammo login (TokenView) da faqat email orqali kiritish imkoniyati bor. Bu mijozlarni tizimga kirishni imkonsiz qiladi.

## Yechim
`BittadaTokenObtainPairSerializer.validate` metodi qayta yozildi:

1. Identifier sifatida `attrs.get('email')` olindi (frontend bu maydonni yuboradi, uning nomi 'email' bo'lsa ham, mijoz telefon raqamini yozishi mumkin).
2. Standart `authenticate(request, email=identifier, password)` bilan sinab ko'riladi.
3. Agar muvaffaqiyatsiz bo'lsa, `User.objects.get(phone=identifier)` orqali telefon raqami bo'yicha qidiradi.
4. Topilgan user_obj parol `check_password` bilan tekshiriladi.
5. Agar topilsa, user o'rnatiladi va token yaratiladi.
6. Parol noto'g'ri yoki user topilmasa, xato qaytariladi.

Bu qisimda `User` modeli import qilindi: `from apps.users.models import User`.

## Xulosa
- Mijozlar endi telefon raqamini login formaga kiritsa, tizimga kira oladi.
- E-mail asosiy identifier bo'lib qoladi, lekin qo'shimcha telefon qo'shildi.
- Token javobida qo'shimcha `redirect` maydon qo'shildi (bu `TokenView` da qo'shilgan).