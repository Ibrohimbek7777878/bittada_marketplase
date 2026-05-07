# Sotuvchi shaxsiy admin paneli (`/dashboard/seller/...`)

**Sana**: 2026-05-05
**Muallif**: Claude (Opus 4.7) — `mebelcityai@gmail.com` so'rovi bo'yicha
**Bosqich**: P0 — Foundation

## Qisqacha

Sotuvchi (seller / internal_supplier) uchun shaxsiy admin panel qo'shildi.
URL prefix: `/dashboard/seller/`. Sotuvchi o'z mahsulotlarini va profilini
boshqaradi (boshqa sellerning mahsulotlariga kira olmaydi — permission check).

### Sahifalar

| URL | View (CBV) | Vazifa |
|-----|------------|--------|
| `/dashboard/seller/` | `SellerDashboardIndexView` | Statistika va so'nggi zakazlar |
| `/dashboard/seller/products/` | `SellerProductListView` | Mahsulotlar ro'yxati (filter+pagination) |
| `/dashboard/seller/products/add/` | `SellerProductCreateView` | Yangi mahsulot yaratish |
| `/dashboard/seller/products/<uuid>/edit/` | `SellerProductUpdateView` | Tahrirlash (faqat o'zining) |
| `/dashboard/seller/profile/edit/` | `SellerProfileEditView` | User+Profile+Avatar tahrirlash |

## O'zgartirilgan / yaratilgan fayllar

| Fayl | Holat | Maqsad |
|------|-------|--------|
| `backend/apps/products/forms.py` | yaratildi | `ProductForm` — rasm upload + 7 ta maydon |
| `backend/apps/users/forms.py` | yaratildi | `SellerProfileForm` — User+Profile+Avatar |
| `backend/apps/products/views.py` | tahrir | 4 ta seller CBV qo'shildi (oxirgi qism) |
| `backend/apps/users/views.py` | tahrir | `SellerProfileEditView` qo'shildi (oxirgi qism) |
| `backend/apps/products/urls.py` | tahrir | `seller_dashboard_urlpatterns` ro'yxati |
| `backend/config/urls.py` | tahrir | `/dashboard/seller/` (management dan oldin) ulandi |
| `backend/templates/dashboard/seller/base_seller.html` | yaratildi | Mustaqil layout (base.html dan extend qilmaydi) |
| `backend/templates/dashboard/seller/index.html` | yaratildi | Umumiy panel: 4 ta stat-card + 5 ta so'nggi |
| `backend/templates/dashboard/seller/products/list.html` | yaratildi | Jadval, status filter, pagination |
| `backend/templates/dashboard/seller/products/form.html` | yaratildi | Add+Edit uchun BITTA shablon |
| `backend/templates/dashboard/seller/profile_edit.html` | yaratildi | Username/avatar/bio formasi |

## Nima uchun?

TZ §6 va §11 bo'yicha sotuvchilar (rolda `seller` yoki `internal_supplier`)
o'z mahsulotlari va profilini mustaqil boshqarishi kerak. Mavjud:

- `apps/management/` — administrator (super_admin/admin) ERP'i. Sotuvchi
  uchun emas (boshqalar mahsulotini ko'radi).
- `apps/products/views.py` ichidagi `product_admin_list_view` —
  `_is_panel_user()` orqali sellerga ham ruxsat bergan, lekin u **butun
  inventarni** ko'rsatadi (boshqa sellerning ham). Sotuvchining shaxsiy
  paneli sifatida ishlamaydi.

Yangi `/dashboard/seller/` esa har bir sotuvchining **faqat o'z** kontentini
ko'rsatadi (`get_queryset` filteri bilan).

## Texnik tafsilotlar

### Permission model

`SellerRequiredMixin` (apps/products/views.py'da):

```python
class SellerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/login/"
    def test_func(self):
        return getattr(self.request.user, "is_seller", False)
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()  # /login/?next=...
        messages.warning(self.request, "Bu sahifa faqat sotuvchilar uchun.")
        return redirect("profile")
```

Test natija:
- Anonymous → `302 → /login/?next=/uz/dashboard/seller/`
- Customer → `302 → /uz/profile/` (warning message bilan)
- Seller → `200`

### Boshqa sellerning mahsulotini tahrirlay olmasligi

`SellerProductUpdateView.get_queryset()`:

```python
def get_queryset(self):
    return Product.objects.filter(seller=self.request.user)
```

Boshqa seller mahsuloti UUID'ini yozsa — `404 Not Found` (chunki queryset
filteri uni topmaydi). Test bilan tasdiqlandi.

### Username o'zgartirilsa public profile darhol yangilanadi

`SellerProfileForm.save()`:

```python
self.user.username = cd["username"]
self.user.save(update_fields=["username"])
```

Test natija:
- POST → `ahmed-seller` → `ahmed-seller-x`
- `GET /u/ahmed-seller-x/` → `200`
- `GET /u/ahmed-seller/` → `404` (eski URL ishlamaydi)

### URL routing tartibi (muhim!)

`config/urls.py`'da `dashboard/seller/` **management'dan oldin** turishi
kerak. Django URL resolutsiyasi top-down: agar `dashboard/` birinchi mos
kelsa va ichida `seller/` topilmasa — 404 qaytaradi (keyingi pattern'larga
o'tmaydi).

```python
path("dashboard/api/v1/", include("apps.management.api_urls")),
path("dashboard/seller/", include((_seller_dashboard_urls, "seller_dashboard"), namespace="seller")),
path("dashboard/", include(("apps.management.urls", "management"), namespace="mgmt")),  # Pastroq
```

### Mahsulot rasmi upload

`apps/media/services.py` bo'sh edi (TZ ko'rsatishicha). Shuning uchun rasm
to'g'ridan-to'g'ri `ProductImage` model orqali saqlanadi (ImageField default
storage backend orqali — local yoki S3). View ichida:

```python
image = form.cleaned_data.get("image")
if image:
    ProductImage.objects.create(product=product, image=image, is_primary=True)
```

`MEDIA_URL` va `MEDIA_ROOT` settings'da sozlangan, debug rejimida
`config/urls.py` orqali static() ham serve qiladi.

### Tahrirlashda yangi rasm yuklash

Eski rasmlar saqlanadi, yangi rasm `is_primary=True` qilib qo'shiladi.
`uniq_primary_image_per_product` constraint sabab eski primary
`is_primary=False` qilib yangilanadi:

```python
ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
ProductImage.objects.create(product=product, image=image, is_primary=True)
```

### `base_seller.html` mustaqilligi

Vazifa cheklovi: "base_erp.html dan EMAS, alohida base_seller.html yasat".
Bunga qo'shimcha: `base.html` ichida `{% url 'auth_logout' %}` mavjud bo'lib,
ushbu URL nomi loyiha urls'da topilmaydi (`apps.products.urls`'da `logout`
nomi bor, lekin `auth_logout` yo'q). Bu mavjud bug — daxlsizlik qoidasi
sabab tegmadik. Shuning uchun `base_seller.html` to'liq mustaqil HTML
hujjat (header/footer/CSS o'zining ichida).

## Test natijalar

```
Anonymous /dashboard/seller/:  302 → /login/?next=/uz/dashboard/seller/
Seller (ahmed-seller):
  /uz/dashboard/seller/:                    200 (12.5 KB)
  /uz/dashboard/seller/products/:           200 (11.9 KB)
  /uz/dashboard/seller/products/add/:       200 (15.1 KB)
  /uz/dashboard/seller/profile/edit/:       200 (15.2 KB)
Customer (sultonbe78) /dashboard/seller/:   302 → /uz/profile/

POST /dashboard/seller/products/add/:       302 → /uz/dashboard/seller/products/
  Products before/after: 0 → 1 ✓

POST /dashboard/seller/profile/edit/:       302 → /uz/dashboard/seller/profile/edit/
  Username: ahmed-seller → ahmed-seller-x ✓
  /uz/u/ahmed-seller-x/:    200 ✓
  /uz/u/ahmed-seller/:      404 ✓ (eski URL endi yo'q)
```

## Qoidalarga muvofiqlik

- ✅ **Daxlsizlik**: mavjud function-based view'lar (product_admin_list_view,
  product_admin_create_view), DRF view'lar va URL'lar o'zgarmagan. `base.html`
  bilan bog'liq mavjud bug'ga tegmadik.
- ✅ **Xavfsizlik**: `LoginRequiredMixin` + `UserPassesTestMixin` har bir
  CBV'da; UpdateView faqat o'z mahsulotini topadi (queryset filter); rasm
  upload `multipart/form-data` + CSRF token.
- ✅ **Tushunarlilik**: barcha yangi qatorlar batafsil izoh bilan.
- ✅ **Hujjatlashtirish**: ushbu fayl + har bir fayl boshida docstring.
- ✅ **README integrity**: README'ga tegmadik.
- ✅ **Vazifa cheklovlari**:
  - `base_erp.html` dan extend qilinmadi (mustaqil base_seller.html)
  - `apps/dashboard/` faqat REST API uchun (kafe), shuning uchun seller
    view'lari `apps/products/` ichida (vazifa ruxsat bergan fallback)
  - Faqat ko'rsatilgan fayllarga tegildi.
