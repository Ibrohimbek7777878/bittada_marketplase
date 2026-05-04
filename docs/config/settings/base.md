# Settings (config/settings/base.py) — o'zgarishlar

## O'zgarish
`MIDDLEWARE` ro'yxatiga yangi middleware qo'shildi:

```python
"apps.users.middleware.BlockCustomerAdminAccessMiddleware",
```

## Joylashuv
`AuthenticationMiddleware` dan keyin, `ManagementAccessMiddleware` dan keyin.

## Maqsad
Mijozlar (role='customer') dan admin panelga (`/admin/` va `/hidden-core-database/`) kirishni cheklash. Bu middleware har bir so'rovda mijozning admin sahifalariga kirishga urinishini aniqlaydi va ularni `/profile/` ga qaytaradi.

## Boshqa o'zgarishlar
Bu faylda boshqa o'zgarishlar yo'q.