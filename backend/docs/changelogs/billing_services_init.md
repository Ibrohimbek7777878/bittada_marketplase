# 📝 O'zgarishlar hisoboti: Billing Servislari (Biznes Mantiq)

## 📅 Sana: 2026-05-01
## 📂 Fayl: `backend/apps/billing/services.py`

---

### 🔍 Nima o'zgardi?
`apps/billing` modulida moliyaviy operatsiyalarni bajaruvchi asosiy funksiyalar (servislar) yozildi:
1.  `create_wallet_for_user`: User uchun hamyon yaratish.
2.  `deposit_to_wallet`: Hamyonni to'ldirish.
3.  `withdraw_from_wallet`: Mablag' yechib olish.
4.  `freeze_funds`: Mablag'ni muzlatish (Escrow uchun).
5.  `unfreeze_funds`: Muzlatishdan chiqarish.

### ❓ Nega o'zgartirildi?
Modellar yaratilgandan so'ng, ularni xavfsiz tarzda boshqaradigan mantiq kerak edi. `TZ_EN.md` dagi barcha moliyaviy ssenariylarni (Section 14 & 15) qo'llab-quvvatlash uchun ushbu servislar majburiy hisoblanadi.

### 🛠️ Qanday muammolar hal qilindi?
1.  **Atomiklik (Data Integrity)**: `transaction.atomic` yordamida pul o'tkazmalarining yarim-chala qolishi oldi olindi.
2.  **Validatsiya**: Balans yetarli bo'lmaganda yoki noto'g'ri qiymatlar kiritilganda xatolik berish tizimi o'rnatildi.
3.  **Auditing**: Har bir servis avtomatik tarzda `Transaction` modelida tarixiy ma'lumot qoldiradi.

### 🔗 Bog'liq fayllar
- `apps/billing/models.py`: Asosiy ma'lumotlar tuzilmasi.
- `apps/escrow/services.py`: Kelgusida ushbu servislar escrow tizimida ishlatiladi.

### 📜 Kod sharhi
Kodning har bir qatori uchun AI va dasturchi tushunishi oson bo'lishi uchun batafsil izohlar qo'shildi.
