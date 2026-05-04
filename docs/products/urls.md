# Products URLs (products/urls.py) — o'zgarishlar

## Umumiy
Yangi view'lar uchun URL yo'llari qo'shildi va mavjud yo'llar o'zgartirildi.

## O'zgarishlar

### 1. Import yangilanishi
`from .views import` ichiga quyidilar qo'shildi:
- `customer_register_view`
- `profile_edit_view`

### 2. Yangi URL pattern'lar

#### `register/customer/`
- **View:** `customer_register_view`
- **Name:** `customer-register`
- **Maqsad:** Mijozlar uchun soddalashtirilgan ro'yxatdan o'tish sahifasi.

#### `profile/edit/`
- **View:** `profile_edit_view`
- **Name:** `profile_edit`
- **Maqsad:** Mijozlar uchun profilni tahrirlash sahifasi (alohida). Asl profil sahifasi `profile/` soddalashtirilgan bo'lib, tahrirlash uchun alohida sahifa taklif qilinadi.

### 3. Mavjud URL (profile/) endi rolga qarab shablon yaratadi
O'zgarishsiz qoldi, lekin ichida shartli logika qo'shildi: mijozlar uchun `customer_profile.html`, boshqalar uchun `profile_erp.html`.

## Eslatma
URL pattern'lari tartibi muhim emas, chunki har biri noyob yo'l. `profile/` va `profile/edit/` bir-biriga aralashmaydi.