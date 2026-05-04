# Products Views (products/views.py) — o'zgarishlar

## Umumiy
Bu fayl template sahifalarini boshqaradigan view'larni o'zgartirdik: `login_view`, `profile_view`, va yangi view'lar qo'shdik.

## 1. login_view — redirect mantiqini o'zgartirish

###olding
Barcha muvaffaqiyatli loginlarni `redirect('home')` ga yo'naltirardi.

###Yangi
Foydalanuvchi rolini tekshiradi:
- `Role.CUSTOMER` → `redirect('profile')`
- `user.is_staff` → `redirect('admin:index')` (Django admin panel)
- boshqalar → `redirect('home')`

Bundan tashqari, telefon raqami orqali login qo'shildi (phone lookup + check_password).

## 2. profile_view — mijozlar uchun soddalashtirilgan shablon

###olding
Barcha foydalanuvchilar uchun `profile_erp.html` (to'liq ERP profil).

###Yangi
Agar `request.user.role == Role.CUSTOMER` bo'lsa, `customer_profile.html` shabloniga o'tadi. Aks holda `profile_erp.html` (to'liq profil). Bu mijozlarning profili soddaroq ko'rinishda bo'lishini ta'minlaydi.

## 3. customer_register_view — yangi view (mijoz ro'yxatdan o'tish)

###Maqsad
Mijozlar uchun alohida, soddalashtirilgan ro'yxatdan o'tish sahifasi.
- Faqat `first_name`, `phone_number`, `password`, `password_confirm` maydonlari.
- Forma validatsiya qilinadi (`CustomerSignupForm`).
- Yaratilgandan so'ng, foydalanuvchi avtomatik login qilinadi va `/profile/` ga yo'naltiriladi.

###Shablon
`customer_register.html` render qilinadi.

## 4. profile_edit_view — profilni tahrirlash sahifasi (alohida)

###Maqsad
Mijozlar uchun "Profilni tahrirlash" tugmasi bosilganda ochiladigan sahifa.
- ongoing `profile_erp.html` shablonidan foydalanadi.
- Bu view faqat tahrirlash uchun; lekin asl profil sahifasi (customer) alohida.

## 5. Import o'zgarishlari
- `from apps.auth_methods.forms import CustomerSignupForm`
- `from apps.users.models import Role, User`

## Xavfsizlik
- Mijozlar `is_staff=False` bilan yaratiladi, shuning uchun admin panelga ruxsat yo'q.
- Middleware orqali qo'shimcha himoya qo'shildi.