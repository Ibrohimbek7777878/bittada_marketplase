# 📝 O'zgarishlar hisoboti: Escrow Servislari (Mablag'larni boshqarish)

## 📅 Sana: 2026-05-01
## 📂 Fayl: `backend/apps/escrow/services.py`

---

### 🔍 Nima o'zgardi?
`apps/escrow` modulida xavfsiz bitimlarni amalga oshiruvchi biznes mantiq (servislar) yaratildi:
1.  `initiate_escrow`: Bitimni boshlash va xaridor pulini muzlatish.
2.  `release_escrow`: Bitim muvaffaqiyatli tugaganda pulni sotuvchiga o'tkazish.
3.  `refund_escrow`: Bitim bekor qilinganda pulni xaridorga qaytarish.

### ❓ Nega o'zgartirildi?
`TZ_EN.md` dagi xavfsiz to'lovlar (Escrow) tizimini real ishlashini ta'minlash uchun ushbu servislar zarur. Ular `billing` moduli bilan uzviy bog'langan holda pul harakatlarini boshqaradi.

### 🛠️ Qanday muammolar hal qilindi?
1.  **Xavfsizlik**: Pulni sotuvchiga darhol bermasdan, platformada "garov" sifatida ushlab turish mexanizmi yaratildi.
2.  **Integratsiya**: `billing` va `escrow` modullari o'rtasidagi bog'liqlik (`freeze`/`unfreeze` servislari orqali) to'g'ri yo'lga qo'yildi.
3.  **Yaxlitlik**: Operatsiyalar atomik tranzaksiyalar ichida bajarilishi ta'minlandi.

### 🔗 Bog'liq fayllar
- `apps/billing/services.py`: Mablag'larni muzlatish va o'tkazish uchun ishlatildi.
- `apps/escrow/models.py`: Escrow holatlarini yangilash uchun ishlatildi.
- `apps/orders/models.py`: Buyurtma ma'lumotlarini olishda foydalanildi.

### 📜 Kod sharhi
Har bir qator dasturchi va AI uchun tushunarli bo'lishi uchun batafsil izohlandi.
