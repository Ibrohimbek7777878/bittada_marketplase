# Standalone (Backendsiz) Rejim hujjatnomasi

## Muammo
Server o'chirilgan holatda yoki internet bo'lmaganda saytda "fetch error" xatoliklari chiqadi va sayt bo'sh bo'lib qoladi.

## Yechim
1.  `frontend_new/src/api/client.js` fayliga `USE_BACKEND` bayrog'i qo'shildi.
2.  Ushbu bayroq `false` qilib belgilandi (Standalone Mode).
3.  Barcha API so'rovlari (login, register, mahsulotlar ro'yxati) endi haqiqiy serverga bormasdan, `demoData.js` dan ma'lumotlarni qaytaradi.
4.  Har bir funksiyaga batafsil kommentariyalar qo'shildi.

## O'zgartirilgan fayllar
- `frontend_new/src/api/client.js`: Backendsiz rejimga o'tkazildi.

## Ta'sir
Sayt endi backend o'chirilgan bo'lsa ham to'liq va xatolarsiz ishlaydi. Bu demo ko'rsatish uchun juda qulay.
