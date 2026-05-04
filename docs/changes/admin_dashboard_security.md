# Admin Dashboard Xavfsizlik yangilanishi hujjatnomasi

## Muammo
Admin dashboard sahifasiga barcha foydalanuvchilar (xatto mehmonlar ham) URL orqali kira olar edi. Bu xavfsizlik nuqtai nazaridan noto'g'ri.

## Yechim
1.  `mountAdminDashboard` funksiyasiga foydalanuvchi huquqlarini tekshirish mantig'i qo'shildi.
2.  Agar foydalanuvchi login qilmagan bo'lsa yoki uning roli `admin` yoki `super_admin` bo'lmasa, u login sahifasiga yo'naltiriladi.
3.  Sayt xavfsizligini ta'minlash uchun `authApi.me()` orqali joriy foydalanuvchi ma'lumotlari tekshiriladi.
4.  Har bir qatorga batafsil kommentariyalar qo'shildi.

## O'zgartirilgan fayllar
- `frontend_new/src/pages/admin-dashboard.js`: Xavfsizlik cheklovlari qo'shildi.

## Ta'sir
Faqat vakolatli shaxslar (adminlar) tizim sozlamalarini o'zgartira oladi.
