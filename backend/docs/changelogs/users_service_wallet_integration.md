# 📝 O'zgarishlar hisoboti: User Servisiga Hamyon Integratsiyasi

## 📅 Sana: 2026-05-01
## 📂 Fayl: `backend/apps/users/services.py`

---

### 🔍 Nima o'zgardi?
`create_user_with_profile` funksiyasi yangilandi: endi foydalanuvchi yaratilayotganda avtomatik ravishda unga tegishli `Wallet` (Hamyon) ham yaratiladi.

### ❓ Nega o'zgartirildi?
`TZ_EN.md` talablariga ko'ra, har bir foydalanuvchi tizimda moliyaviy operatsiyalarni bajarish imkoniyatiga ega bo'lishi kerak. Hamyonni ro'yxatdan o'tish vaqtida avtomatik yaratish orqali foydalanuvchi uchun "frictionless" (to'siqlarsiz) tajriba ta'minlanadi.

### 🛠️ Qanday muammolar hal qilindi?
1.  **Avtomatlashtirish**: Hamyonni qo'lda yaratish zarurati qolmadi.
2.  **Yaxlitlik (Integrity)**: `transaction.atomic` tufayli yoki hamma narsa (User + Profile + Wallet) yaratiladi, yoki birontasi yaratilmaydi. Bu ma'lumotlar bazasida "yetim" qolgan userlar bo'lishini oldini oladi.

### 🔗 Bog'liq fayllar
- `apps/billing/services.py`: `create_wallet_for_user` funksiyasi chaqirildi.
- `apps/users/models.py`: User va Profile modellari.

### 📜 Kod sharhi
O'zgartirilgan har bir qator uchun o'zbek tilida batafsil izohlar qo'shildi.
