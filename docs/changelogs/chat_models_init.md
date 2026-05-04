# 📝 O'zgarishlar hisoboti: Chat Modeli (Yozishmalar)

## 📅 Sana: 2026-05-01
## 📂 Fayl: `backend/apps/chat/models.py`

---

### 🔍 Nima o'zgardi?
`apps/chat` modulida real vaqtda muloqot qilish uchun asosiy modellar yaratildi:
1.  **ChatRoom**: Foydalanuvchilar o'rtasidagi dialog xonasi.
2.  **Message**: Yozishmalar va ularga biriktirilgan fayllar.

### ❓ Nega o'zgartirildi?
`TZ_EN.md` (17-bo'lim) talablariga ko'ra, xaridor va sotuvchi o'rtasida to'g'ridan-to'g'ri muloqot (Direct Messages) va buyurtmalar yuzasidan yozishmalar imkoniyati bo'lishi shart.

### 🛠️ Qanday muammolar hal qilindi?
1.  **Dialog boshqaruvi**: Foydalanuvchilar o'rtasidagi xabarlarni guruhlash uchun xonalar tizimi (`ChatRoom`) joriy etildi.
2.  **Kontekstli muloqot**: Chatni aniq bir buyurtma (`Order`) bilan bog'lash imkoniyati orqali qo'llab-quvvatlash va savdo jarayoni osonlashtirildi.
3.  **Media almashinuvi**: Xabarlarga fayllar biriktirish (`attachment`) imkoniyati qo'shildi.

### 🔗 Bog'liq fayllar
- `apps/users/models.py`: Ishtirokchilarni aniqlashda foydalanildi.
- `apps/orders/models.py`: Buyurtma bilan bog'lashda foydalanildi.

### 📜 Kod sharhi
Har bir qator dasturchi va AI uchun tushunarli bo'lishi uchun batafsil izohlandi.
