# 📝 O'zgarishlar hisoboti: Billing Modeli (Hamyon va Tranzaksiya)

## 📅 Sana: 2026-05-01
## 📂 Fayl: `backend/apps/billing/models.py`

---

### 🔍 Nima o'zgardi?
`apps/billing` modulida loyihaning moliyaviy poydevori hisoblangan **Wallet** (Hamyon) va **Transaction** (Tranzaksiya) modellari yaratildi.

### ❓ Nega o'zgartirildi?
`TZ_EN.md` (14-bo'lim) talablariga ko'ra, har bir foydalanuvchi platformada shaxsiy hamyoniga ega bo'lishi va barcha operatsiyalar (to'lovlar, muzlatishlar, yechib olishlar) audit qilinishi shart. Hozirgacha bu modul faqat bo'sh papka ko'rinishida edi.

### 🛠️ Qanday muammolar hal qilindi?
1.  **Mablag'larni boshqarish**: Foydalanuvchilar balansini xavfsiz saqlash uchun `Wallet` modeli kiritildi.
2.  **Audit va Tarix**: Har bir pul harakatini kuzatish uchun `Transaction` modeli orqali tarixni saqlash imkoniyati yaratildi.
3.  **Muzlatish (Freeze) mantiqi**: Savdo va Escrow (Section 15) tizimi uchun pullarni vaqtincha muzlatib qo'yish maydoni (`frozen_balance`) qo'shildi.

### 🔗 Bog'liq fayllar
- `core/models.py`: `BaseModel` dan meros olingan.
- `users/models.py`: Foydalanuvchi bilan `OneToOne` bog'langan.

### 📜 Kod sharhi
Barcha kod qatorlari uzbek tilida batafsil izohlar bilan yozildi, bu esa AI va boshqa dasturchilarga mantiqni tez tushunishga yordam beradi.
