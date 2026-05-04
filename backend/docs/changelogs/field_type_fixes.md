# 📝 O'zgarishlar hisoboti: Field turi xatoliklarini tuzatish

## 📅 Sana: 2026-05-01
## 📂 Fayllar: `apps/escrow/models.py`, `apps/billing/models.py`

---

### 🔍 Nima o'zgardi?
`Escrow` va `Transaction` modellaridagi `CharField` maydonlarida xato yozilgan `max_digits` va `decimal_places` argumentlari olib tashlandi va `max_length` bilan almashtirildi.

### ❓ Nega o'zgartirildi?
Django-da `max_digits` faqat `DecimalField` uchun amal qiladi. `CharField` da bu argumentning bo'lishi `TypeError: Field.__init__() got an unexpected keyword argument 'max_digits'` xatosini keltirib chiqaradi va migratsiyalarni to'xtatib qo'yadi.

### 🛠️ Qanday muammolar hal qilindi?
1.  **Migratsiya xatosi**: Loyihaning ma'lumotlar bazasi migratsiyalari endi muvaffaqiyatli ishlaydi.
2.  **Validatsiya**: Maydonlar Django standartlariga muvofiq to'g'ri sozladi.

### 🔗 Bog'liq fayllar
- `apps/escrow/models.py`: `status` maydoni tuzatildi.
- `apps/billing/models.py`: `kind`, `status` va `external_id` maydonlari tuzatildi.

### 📜 Kod sharhi
Har bir tuzatilgan qator uchun batafsil izohlar qo'shildi.
