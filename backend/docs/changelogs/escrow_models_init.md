# 📝 O'zgarishlar hisoboti: Escrow Modeli (Xavfsiz bitimlar)

## 📅 Sana: 2026-05-01
## 📂 Fayl: `backend/apps/escrow/models.py`

---

### 🔍 Nima o'zgardi?
`apps/escrow` modulida xavfsiz bitimlarni boshqaruvchi **Escrow** modeli yaratildi.

### ❓ Nega o'zgartirildi?
`TZ_EN.md` (15-bo'lim) talablariga ko'ra, xaridor va sotuvchi o'rtasidagi bitimlar xavfsiz bo'lishi, ya'ni xaridor mahsulotni olganini tasdiqlamaguncha pul sotuvchiga o'tkazilmasligi kerak. Ushbu model bitim holatini kuzatib boradi.

### 🛠️ Qanday muammolar hal qilindi?
1.  **Ishonch (Trust)**: Xaridor pullari platformada xavfsiz saqlanishini ta'minlash uchun `HELD` holati joriy etildi.
2.  **Bahsli holatlar**: Agar bitimda muammo bo'lsa, uni `DISPUTED` holatiga o'tkazish imkoniyati yaratildi.
3.  **Buyurtma bilan bog'liqlik**: Har bir bitim konkret buyurtma bilan uzviy bog'landi.

### 🔗 Bog'liq fayllar
- `apps/orders/models.py`: Buyurtma (Order) modeli bilan bog'langan.
- `apps/users/models.py`: Buyer va Seller rollari bilan ishlaydi.
- `apps/billing/models.py`: Mablag'larni muzlatish mantiqi bilan ishlaydi.

### 📜 Kod sharhi
Har bir qator uchun o'zbek tilida batafsil izohlar qo'shildi.
