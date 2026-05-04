# Auth Methods Views (auth_methods/views.py) — o'zgarishlar

## Umumiy
O'zgarishlar: `RegisterView` va `TokenView` qismlariga yangi mantiq qo'shildi.

## 1. RegisterView — mijozlar uchun redirect o'zgartirildi

###olding holat
- customer → '/' (bosh sahifa)
- seller → '/services/'
- internal_supplier → '/profile/'

###Yangi holat
- customer → '/profile/' (mijoz profil sahifasiga)
- seller → '/services/'
- internal_supplier → '/profile/'
- boshqalar → '/' (fallback)

###Amal
`if user.role == Role.CUSTOMER: redirect_url = '/profile/'` qo'shildi.

## 2. TokenView — Login (JWT) endpointiga redirect qo'shildi

###olding holat
JWT token qaytargan, session yozilgan, lekin redirect yo'q. Frontend har doim '/' ga yo'naltiardi.

###Yangi holat
Muvaffaqiyatli login dan so'ng, foydalanuvchi roliga qarab `response.data['redirect']` da qaytariladi:
- customer → '/profile/'
- is_staff (admin) → '/hidden-core-database/'
- boshqalar → '/'

###Amal
TokenView.post metodida `user` aniqlanib, uning role/ is_staff ga qarab `redirect_url` hisoblanadi va `response.data['redirect']` ga qo'shiladi. Bu frontend (pages/login.html) ga olib boradigan yo'lni aniqlash imkonini beradi.

## 3. BittadaTokenObtainPairSerializer — phone-based login qo'shildi

###olding
Faqat `email` orqali autentifikatsiya.

###Yangi
Serializer `validate` metodi qayta yozildi:
- `identifier = attrs.get('email')` (login formidagi maydon)
- Avval `authenticate(request, email=identifier, password)` bilan sinab ko'riladi.
- Agar muvaffaqiyatsiz bo'lsa, `User.objects.get(phone=identifier)` orqali telefon raqami bo'yicha qidiradi.
- Parol `check_password` bilan tekshiriladi.
- Agar topilsa, user o'rnatiladi va token yaratiladi.

Bu mijozlar telephone orqali kirishlarini ta'minlaydi.

## Xavfsizlik
- Mijozlar (CUSTOMER) admin yo'nalishlariga bloklanadi (middleware orqali, alohida).
- Parol uzunligi min 6 belgi (serializer da).