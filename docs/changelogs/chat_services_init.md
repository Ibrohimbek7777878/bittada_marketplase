# 📝 O'zgarishlar hisoboti: Chat Servislari (Xabar almashish mantiqi)

## 📅 Sana: 2026-05-01
## 📂 Fayl: `backend/apps/chat/services.py`

---

### 🔍 Nima o'zgardi?
`apps/chat` modulida yozishmalarni boshqarish uchun servislar yaratildi:
1.  `get_or_create_direct_room`: Ikki foydalanuvchi o'rtasida chat xonasini ochish yoki topish.
2.  `send_message`: Xabarlarni yuborish va xona vaqtini yangilash.
3.  `mark_messages_as_read`: Xabarlarni o'qilgan deb belgilash.

### ❓ Nega o'zgartirildi?
Modellar yaratilgandan so'ng, real foydalanuvchilar o'rtasida xavfsiz va mantiqiy xabar almashish jarayonini ta'minlash uchun ushbu servislar zarur edi.

### 🛠️ Qanday muammolar hal qilindi?
1.  **Duplicate xonalar**: Ikki user o'rtasida bitta buyurtma uchun faqat bitta xona bo'lishi ta'minlandi.
2.  **Xavfsizlik**: Xonada bo'lmagan foydalanuvchi nomidan xabar yuborish taqiqlandi.
3.  **Holat boshqaruvi**: Xabarlarning o'qilgan/o'qilmagan holatini yangilash mantiqi markazlashtirildi.

### 🔗 Bog'liq fayllar
- `apps/chat/models.py`: Chat va Message modellari.
- `apps/users/models.py`: Foydalanuvchi verifikatsiyasi.

### 📜 Kod sharhi
Har bir qator dasturchi va AI uchun tushunarli bo'lishi uchun batafsil izohlandi.
