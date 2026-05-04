# 📝 O'zgarishlar hisoboti: Billing Selektorlari (O'qish logikasi)

## 📅 Sana: 2026-05-01
## 📂 Fayl: `backend/apps/billing/selectors.py`

---

### 🔍 Nima o'zgardi?
`apps/billing` modulida ma'lumotlarni o'qish uchun maxsus selektorlar yaratildi:
1.  `get_wallet_for_user`: User hamyonini topish.
2.  `get_wallet_balance`: Joriy balansni olish.
3.  `get_frozen_balance`: Muzlatilgan balansni olish.
4.  `get_user_transaction_history`: Tranzaksiyalar tarixini olish.
5.  `get_transaction_by_external_id`: Tashqi ID bo'yicha qidirish.

### ❓ Nega o'zgartirildi?
Loyihaning arxitektura talabiga ko'ra, ma'lumotlarni o'qish logikasi (selectors) yozish logikasidan (services) alohida bo'lishi kerak. Bu kodni toza saqlash va testlashni osonlashtirish uchun zarur.

### 🛠️ Qanday muammolar hal qilindi?
1.  **Kod takrorlanishi**: Hamyonni qidirish mantiqi bitta joyga jamlandi.
2.  **Optimallashtirish**: Tranzaksiyalar tarixini limit bilan olish va tartiblash markazlashtirildi.
3.  **Xavfsizlik**: `get_object_or_404` yordamida mavjud bo'lmagan hamyonlar uchun to'g'ri xatolik qaytarish ta'minlandi.

### 🔗 Bog'liq fayllar
- `apps/billing/models.py`: Ma'lumotlar manbai.
- `apps/billing/views.py`: Kelgusida ushbu selektorlar API ko'rinishlarida ishlatiladi.

### 📜 Kod sharhi
Har bir qator uchun o'zbek tilida batafsil tushuntirishlar berildi.
