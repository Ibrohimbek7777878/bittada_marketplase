# PageContent Model Update

## Muammo
Saytdagi barcha matnlar va yozuvlar (statik kontent) qattiq kodlangan (hardcoded) edi. Admin ularni saytni o'zidan o'zgartira olmas edi.

## Yechim
1.  `apps.pages.models.PageContent` modeli yaratildi. Bu model `key` (kalit), `value` (qiymat) va `language` (til) maydonlarini o'z ichiga oladi.
2.  Admin panel orqali har bir yozuvni (masalan, `hero_title`) har xil tillar uchun tahrirlash imkoniyati yaratildi.
3.  Kod qatorlariga batafsil kommentariyalar qo'shildi.

## O'zgartirilgan fayllar
- `backend/apps/pages/models.py`: Yangi model qo'shildi.

## Ta'sir
Endi saytdagi barcha matnlarni backend orqali dinamik boshqarish mumkin.
