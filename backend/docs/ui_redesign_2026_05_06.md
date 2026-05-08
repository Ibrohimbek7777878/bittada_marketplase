# UI qayta dizayn — 2026-05-06

> README qoidasi #3: Har bir o'zgartirish uchun alohida `.md` hujjat. Bu fayl bugungi UI rejasi va backend modellaridagi o'zgarishlarni bayon qiladi.

## Maqsad (foydalanuvchi talabi)

1. Asosiy navigatsiya menyusi **yon tomonga** ko'chirilsin (chap chetda).
2. **Hover** asosida ochilsin — mishka chap chetga olib kelganda kengayadi, olib chiqilganda yana ingichka chiziq holatiga qaytadi.
3. **Yuqori menyu** minimallashtirilsin: faqat 5 element qoladi:
   - Logo + brend nomi (Bittada)
   - Qidiruv inputi
   - Kun/tun rejimi (theme toggle)
   - Saqlangan e'lonlar tugmasi (SavedProduct)
   - Savatcha tugmasi
4. "Mahsulotlar" tugmasi `/products/` sahifasini ochsin.
5. Backend modellar yetishmayotgan bo'lsa qo'shilsin: SavedProduct, ProductComment, ProductCommentImage.
   - **Muhim:** sharhga rasm `image = ImageField(...)` to'g'ridan-to'g'ri qo'yilmasin — Productning o'z `ProductImage`'i bor, chalkashish ehtimoli bor. Sharh rasmi alohida `ProductCommentImage` modeli orqali bog'lanadi.

## Bajarilgan ishlar

### A. Backend modellar

#### 1) [`apps.marketplace.SavedProduct`](apps/marketplace/models.py)

Foydalanuvchi saqlagan mahsulotlar (favorites/wishlist).

```python
class SavedProduct(BaseModel):
    user = FK(User, related_name="saved_products")
    product = FK(Product, related_name="saved_by_users")
    note = CharField(max_length=200, blank=True)  # shaxsiy izoh
```

- `UniqueConstraint(user, product)` — bir foydalanuvchi bir mahsulotni faqat bir marta saqlaydi.
- `Index(user, -created_at)` — eng yangi saqlanganlarni tez olish uchun.
- DB jadval: `marketplace_saved_product`.

#### 2) [`apps.products.ProductComment`](apps/products/models.py)

Mahsulotga foydalanuvchi sharhi (1–5 yulduz reyting + matn).

```python
class ProductComment(BaseModel):
    product = FK(Product, related_name="comments")
    author = FK(User, related_name="product_comments")
    parent = FK("self", null=True, related_name="replies")  # reply daraxti
    rating = PositiveSmallIntegerField(choices=[0–5])
    body = TextField()
    status = CharField(choices=APPROVED/PENDING/REJECTED, default=APPROVED)
    is_verified_buyer = BooleanField(default=False)
    helpful_count = PositiveIntegerField(default=0)  # denormalized
```

- `parent` orqali javob (reply) tizimi.
- Modarator status — APPROVED/PENDING/REJECTED.
- DB jadval: `products_product_comment`.

#### 3) [`apps.products.ProductCommentImage`](apps/products/models.py)

Sharhga biriktirilgan rasm (alohida model — Product'ning `ProductImage`'i bilan chalkashtirilmasligi uchun).

```python
class ProductCommentImage(BaseModel):
    comment = FK(ProductComment, related_name="images")
    image = ImageField(upload_to="products/comments/%Y/%m/")
    alt_uz / alt_ru / alt_en = CharField
    order = PositiveSmallIntegerField
```

- DB jadval: `products_product_comment_image` (ProductImage'nikidan farqli).
- Yuklash papkasi `products/comments/...` (ProductImage `products/images/...` dan ajralgan).
- Bir sharhga 0..N ta rasm.

### B. URL va view

#### Yangi `/products/` sahifa

[`apps/products/views.py`](apps/products/views.py) ga `products_list_view` qo'shildi:

- Faqat `status=PUBLISHED` mahsulotlar.
- `?category=<slug>` va `?q=<search>` query parametrlarini qabul qiladi.
- `select_related("category").prefetch_related("images")` — N+1 query oldini olinadi.
- Birinchi 60 ta natija (paginatsiya keyinroq).
- Mavjud `templates/shop_erp.html` shabloni ishlatiladi.

[`apps/products/urls.py`](apps/products/urls.py) ga qo'shilgan:

```python
path("products/", products_list_view, name="products_list"),
```

URL reverse: `reverse('products_list')` → `/uz/products/`.

### C. UI — yangi navbar

[`templates/includes/erp_navbar.html`](templates/includes/erp_navbar.html) **to'liq qayta yozildi**.

Eski version (saqlandi git history'da): Catalog mega-menu, central nav (4 link), notifications, lang switcher, profile, mobile burger — barchasi olindi.

Yangi minimal struktura:

| Joy | Element | Funksiya |
|-----|---------|----------|
| Chap | Logo aylana + "Bittada" | `/` ga link |
| Markaz | Qidiruv inputi | `/products/?q=...` ga GET |
| O'ng | Theme toggle 🌙/☀️ | localStorage da saqlanadi |
| O'ng | Saqlangan e'lonlar 🔖 | `/wishlist/` |
| O'ng | Savatcha 🛒 | `/cart/` |
| O'ng | Profil/Login | auth holatiga qarab |

- Theme toggle: `data-theme="light"` ↔ `data-theme="dark"` html attributini almashtiradi, `localStorage['bittada-theme']` ga saqlaydi.
- Dark mode CSS — navbar va search input uchun qo'shildi.
- Mobile (< 640px) — brand text yashiriladi, qidiruv qisqaradi.

### D. UI — yangi yon menyu (hover bilan ochiladigan)

Yangi fayl: [`templates/includes/erp_public_sidebar.html`](templates/includes/erp_public_sidebar.html).

**Eski `erp_sidebar.html` saqlandi** (ERP /dashboard/* sahifalarida ishlash davom etadi) — README qoidasi #1 (mavjud kodga zarar yetkazmaslik).

Asosiy g'oya:
- `position: fixed; left: 0; width: 8px;` — default holatda ingichka chiziq.
- `:hover { width: 280px; }` — mishka kelganda 280 piksel ga kengayadi (CSS transition 280ms).
- `:focus-within` — klaviatura accessibility uchun ham ishlaydi.
- Mobile (< 768px) — hover yo'q, `is-open` klassi orqali ochiladi (kelajakda burger trigger qo'shiladi).

Ichidagi havolalar:

| Guruh | Havola | URL |
|-------|--------|-----|
| Asosiy | Bosh sahifa | `/` |
| Asosiy | Mahsulotlar | `/products/` |
| Asosiy | Showroom (3D) | `/showroom/` |
| Asosiy | Xizmatlar | `/services/` |
| Asosiy | Ishlab chiqarish | `/manufacturing/` |
| Asosiy | Ishlab chiqaruvchilar | `/manufacturers/` |
| Mening hisobim* | Profil | `/profile/` |
| Mening hisobim* | Buyurtmalar | `/orders/` |
| Mening hisobim* | Saqlangan e'lonlar | `/wishlist/` |
| Mening hisobim* | Savatcha | `/cart/` |
| Platforma | Kompaniya haqida | `/company/` |
| Platforma | Escrow Fund | `/escrow/` |
| Boshqaruv** | Command Center | `/dashboard/` |
| Oxirida | Chiqish/Kirish | `/logout/` yoki `/login/` |

*\* faqat tizimga kirgan foydalanuvchiga; \*\* faqat is_superuser*

Active link: `request.path` solishtirildi va `.active` klassi qo'yiladi (yashil fon + oq matn).

### E. base_erp.html

[`templates/base_erp.html`](templates/base_erp.html) yangilandi:

```diff
+ {% include 'includes/erp_public_sidebar.html' %}  # har doim, public
- {% if user.is_authenticated %}
-     {% include 'includes/erp_sidebar.html' %}
- {% endif %}
+ {% if user.is_authenticated and '/dashboard' in request.path %}
+     {% include 'includes/erp_sidebar.html' %}
+ {% endif %}
```

`erp-layout` ga `padding-left: 8px` qo'shildi (sidebar trigger uchun joy).

## Tekshirish

```bash
$ python manage.py makemigrations
Migrations for 'products':
  0007_productcomment_productcommentimage_and_more.py
Migrations for 'marketplace':
  0002_savedproduct_and_more.py

$ python manage.py migrate
Applying products.0007_productcomment_productcommentimage_and_more... OK
Applying marketplace.0002_savedproduct_and_more... OK

$ python manage.py check
System check identified 1 issue (0 silenced).
[Faqat bog'liq emas: staticfiles.W004 — 'static' papkasi yo'q.]

$ python -c "from django.urls import reverse; print(reverse('products_list'))"
/uz/products/
```

## Yaratilgan/o'zgartirilgan fayllar

```
backend/apps/marketplace/models.py           [+ SavedProduct]
backend/apps/marketplace/migrations/0002_savedproduct_and_more.py        [yangi]

backend/apps/products/models.py              [+ ProductComment + ProductCommentImage]
backend/apps/products/migrations/0007_productcomment_productcommentimage_and_more.py  [yangi]

backend/apps/products/views.py               [+ products_list_view]
backend/apps/products/urls.py                [+ /products/]

backend/templates/includes/erp_navbar.html              [to'liq qayta yozildi]
backend/templates/includes/erp_public_sidebar.html      [yangi fayl]
backend/templates/base_erp.html              [public sidebar har doim, ERP sidebar /dashboard/ da]

backend/docs/ui_redesign_2026_05_06.md       [bu hujjat]
```

## Hech narsa buzilmadi

- Eski `erp_sidebar.html` (ERP /dashboard/) — TEGILMADI, /dashboard/* sahifalarda hali ham ishlaydi.
- Eski `Cart`, `CartItem` — komment qo'shildi, lekin field yoki Meta o'zgartirilmadi.
- Eski 4 ta navigatsiya havolasi (home/showroom/services/manufacturing) — yon menyuga ko'chirildi, URL nomlari saqlandi.
- `ProductImage`, `ProductFile`, `Category.cover_image` va boshqa eski rasm modellari — TEGILMADI.

## Keyingi qadamlar (foydalanuvchi 1tama-1ta beradi)

Foydalanuvchi: "buni qil va davomini keyin men bittama bitta berib ketaman"

Hozirgi holat — tayyor poydevor:
- `/products/` mahsulotlar listi ishlaydi ([shop_erp.html](templates/shop_erp.html) bilan).
- Yon menyu hover bilan ochiladi.
- Yuqori menyu minimal.
- Theme toggle tayyor.
- Backend modellar (Saved + Comment + CommentImage) tayyor.

Kelgusi sahifalar (kutilayotgan):
- `cart_erp.html` to'liq ulanishi (CartItem CRUD endpointlari).
- `wishlist_erp.html` to'liq ulanishi (SavedProduct CRUD endpointlari).
- `product_detail_erp.html` ga sharhlar bo'limini qo'shish (ProductComment listing + form).
- `home_erp.html` da yangi navbar/sidebar ga moslashish (kerak bo'lsa).
- Boshqa `*_erp.html` har biri navigatsiyaga to'g'ri ulanganini tekshirish.
