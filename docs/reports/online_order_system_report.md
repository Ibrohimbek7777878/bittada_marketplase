# Bittada Marketplace: Online Buyurtma Tizimi Hisoboti

Ushbu hisobot Bittada Marketplace loyihasida online buyurtma berish tizimini to'liq ishga tushirish bo'yicha amalga oshirilgan ishlarni tavsiflaydi.

## Amalga oshirilgan o'zgarishlar

### 1. Savatcha Tizimi (Cart Logic)
- `apps.marketplace` app'ida `Cart` va `CartItem` modellari yaratildi.
- Mahsulotni savatchaga qo'shish (`AddToCartView`), ko'rish (`CartView`) va o'chirish (`RemoveFromCartView`) API'lari yaratildi.
- Mahsulot detali sahifasida (`product_detail_erp.html`) "Savatchaga qo'shish" tugmasi API bilan bog'landi.

### 2. Checkout va Buyurtma Berish
- `/checkout/` sahifasi yaratildi (`checkout_erp.html`).
- Foydalanuvchi ma'lumotlari (ism, tel) va savatchadagi mahsulotlar ko'rinadigan qilib sozlandi.
- `CreateOrderView` API'si orqali `Order` va `OrderItem` obyektlarini yaratish mantiqi joriy qilindi.
- Buyurtma berilgandan so'ng savatchani tozalash va `/orders/` sahifasiga yo'naltirish amalga oshirildi.

### 3. Ombor (Stock) Boshqaruvi
- `apps.marketplace.signals` moduli yaratildi.
- `post_save` signali orqali buyurtma qilingan mahsulot miqdori avtomatik ravishda `Product.stock_qty` dan ayirib tashlanadigan qilindi.
- Agar mahsulot soni 0 bo'lsa, `is_in_stock` flag'i avtomatik `False` holatiga o'tadi.

### 4. Admin Panel va Foydalanuvchilar
- `UserAdmin` (Admin panel) TZ talablari bo'yicha sozlandi:
    - Birinchi ustunda foydalanuvchi `ID` si ko'rsatildi.
    - Keyin `Ism`, `Telefon`, `Rol` va `Buyurtmalar soni` ustunlari qo'shildi.
    - Qidiruv tizimi `ID`, `Ism`, `Tel` bo'yicha ishlashi ta'minlandi.
- Mijoz registratsiyasi ism va telefon raqami orqali ishlashi ta'minlandi.

## Muhim Texnik Ma'lumotlar
- **Modellar**: `Cart`, `CartItem` (apps.marketplace)
- **API Endpointlar**:
    - `POST /api/v1/marketplace/cart/add/`
    - `GET /api/v1/marketplace/cart/`
    - `POST /api/v1/marketplace/order/create/`
- **Signal**: `OrderItem` saqlanganda `Product.stock_qty` ni yangilaydi.

## Xulosa
Online buyurtma berish tizimi to'liq va xavfsiz holda ishga tushirildi. Barcha amallar loyiha qoidalariga (README.md) va texnik topshiriqqa (TZ_EN.md) muvofiq bajarildi.
