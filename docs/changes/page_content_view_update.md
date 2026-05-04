# Pages Views uchun o'zgarishlar hujjatnomasi

## Muammo
`PageContentViewSet` standart `ModelViewSet`dan foydalanar edi. Admin panelda bir xil kalitli matnni saqlamoqchi bo'lganda (POST so'rovi orqali), bazada unikal kalit (unique_together) bo'lgani uchun xatolik yuz berar edi.

## Yechim
1.  `PageContentViewSet` dagi `create` metodi qayta yozildi.
2.  `update_or_create` mantiqi qo'shildi: agar berilgan kalit va til bo'yicha matn mavjud bo'lsa - u yangilanadi, bo'lmasa - yangisi yaratiladi.
3.  Har bir kod qatoriga batafsil kommentariyalar qo'shildi.

## O'zgartirilgan fayllar
- `backend/apps/pages/views.py`: `create` metodi yangilandi.

## Ta'sir
Admin panelda matnlarni saqlashda hech qanday xatolik yuz bermaydi va ma'lumotlar to'g'ri yangilanadi.
