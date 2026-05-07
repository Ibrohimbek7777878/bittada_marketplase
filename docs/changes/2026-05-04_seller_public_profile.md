# Sotuvchi public profile sahifasi (`/u/<username>/`)

**Sana**: 2026-05-04
**Muallif**: Claude (Opus 4.7) — `mebelcityai@gmail.com` so'rovi bo'yicha
**Bosqich**: P0 — Foundation

## Qisqacha

Sotuvchi (seller / internal_supplier) uchun Instagram-uslubdagi unikal public
profile sahifasi qo'shildi. URL: `/u/<username>/`. Sahifa avtomatik ravishda
ikkita tab ko'rsatadi:

- **Mahsulotlar** — agar sotuvchi mahsulot qo'shgan bo'lsa
- **Portfolio** — agar sotuvchi portfolio qo'shgan bo'lsa

Agar ikkalasi ham bo'lsa — ikkala tab birga chiqadi va vanilla JS bilan
sahifa qayta yuklanmasdan switch qiladi.

## O'zgartirilgan / yaratilgan fayllar

| Fayl | Holat | Maqsad |
|------|-------|--------|
| `backend/apps/showroom/models.py` | tahrir | `PortfolioItem` modeli qo'shildi |
| `backend/apps/showroom/migrations/0001_initial.py` | yaratildi | Yangi jadval (PortfolioItem) |
| `backend/apps/showroom/admin.py` | tahrir | `PortfolioItemAdmin` registratsiyasi |
| `backend/apps/showroom/selectors.py` | tahrir | `get_portfolio_by_seller(seller_id)` funksiyasi |
| `backend/apps/products/selectors.py` | tahrir | `get_products_by_seller(seller_id)` funksiyasi |
| `backend/apps/users/views.py` | tahrir | `SellerPublicProfileView` (TemplateView CBV) qo'shildi |
| `backend/apps/users/urls.py` | tahrir | `public_template_urlpatterns` ro'yxati qo'shildi |
| `backend/config/urls.py` | tahrir | `template_patterns` ga `/u/<username>/` ulandi |
| `backend/templates/profile/public_profile.html` | yaratildi | Asosiy sahifa shabloni |
| `backend/templates/profile/tabs/products_tab.html` | yaratildi | Mahsulotlar fragment |
| `backend/templates/profile/tabs/portfolio_tab.html` | yaratildi | Portfolio fragment |
| `backend/templates/includes/seller_card.html` | yaratildi | Qayta ishlatiladigan seller kartochkasi |

## Nima uchun?

TZ §6 va §7 bo'yicha sotuvchilar (rolda `seller` yoki `internal_supplier`
bo'lganlar) uchun ochiq ko'rinishdagi profil sahifasi kerak edi. Eski
`apps/products/views.py` ichidagi `seller_profile_view` mavjud edi, lekin u:

- Kontrakt jihatdan qarama-qarshi (Products app'da User'ning sahifasi)
- Portfolio kontentini qo'llab-quvvatlamasdi
- URL `/api/v1/users/u/<username>/template/` — Instagram-uslubdan uzoq

Yangi yondashuv:

- View **users** app'da (mantiqan to'g'ri joy)
- Mahsulotlar va Portfolio bitta sahifada (TZ talabi: 3 yoki 4 turdagi layout)
- URL `/u/<username>/` — qisqa, eslab qolish oson
- Eski `seller_profile_view` o'chirilmadi (daxlsizlik qoidasi) — parallel ishlaydi

## Qanday muammo hal qilindi?

1. **Sotuvchi uchun yagona "vizit kartochka" yo'q edi.** Endi har bir seller
   o'z `@username` orqali topiladi.
2. **Portfolio modeli umuman yo'q edi** (showroom/models.py bo'sh edi). Endi
   `PortfolioItem` orqali ish namunalari katalogi bor.
3. **Mahsulot va portfolioni alohida ko'rsatish kerak edi** — ikkita tab.

## Texnik tafsilotlar

### URL routing

`apps/users/urls.py` ichida ikki qatlam:

```python
urlpatterns = [...]                      # API uchun (/api/v1/users/...)
public_template_urlpatterns = [          # Yangi: HTML sahifa uchun
    path("u/<str:username>/", SellerPublicProfileView.as_view(), name="seller-public-profile"),
]
```

`config/urls.py` ichida:

```python
from apps.users.urls import public_template_urlpatterns as _user_public_urls
template_patterns = [
    ...
    *_user_public_urls,   # i18n_patterns ichida → /uz/u/..., /ru/u/..., /en/u/...
]
```

### View mantig'i

`SellerPublicProfileView(TemplateView)`:

1. `get_object_or_404` — username bo'yicha User, topilmasa 404
2. `is_seller` tekshiruvi — customer profili yo'q (Http404)
3. `profile.visibility == PUBLIC` — yashirin/private profillar 404
4. Selektorlar orqali products va portfolio QuerySet
5. `has_products` / `has_portfolio` flaglari — tab ko'rsatish uchun
6. `active_tab` — boshlang'ich tanlangan tab

### Tab switching

Vanilla JS (HTMX yoki JS framework emas — TZ talabi minimallikni saqlash).
`data-tab` attributi orqali switch qiladi, `aria-selected` va `.active`
klasslarini almashtiradi.

### Mobile-first responsive

- 96px avatar (mobil) → 150px (desktop, ≥736px)
- 1 ustun → ikki ustun yon-yon
- Grid: 2 ustun (mobil) → 3 ustun (≥640px)

## Test qilish

```bash
# 1. Migration apply
./venv/bin/python manage.py migrate showroom

# 2. Sistem tekshiruvi
./venv/bin/python manage.py check     # 0 issues

# 3. Mavjud bo'lmagan user → 404
curl -i http://127.0.0.1:8000/uz/u/no-such/

# 4. Mavjud sotuvchi → 200 + HTML
curl -i http://127.0.0.1:8000/uz/u/ahmed-seller/
```

Test natija: 404 va 200 statuslar to'g'ri ishladi. HTML — 58KB.

## Kelajak ishlar (out of scope)

- Portfolio detail sahifasi (hozircha karta hover bilan tavsif beradi)
- Sotuvchining oldingi ishlari uchun Yandex/Google Maps integratsiyasi
- Profile sahifaga kirish statistikasi (Profile.profile_views inkrement)
- Dropdown filter (mahsulotlarni kategoriyasi bo'yicha tablar ichida)

## Qoidalarga muvofiqlik

- ✅ **Daxlsizlik**: mavjud `PublicProfileView` (DRF), `seller_profile_view`
  (eski template) va `users/urlpatterns` o'zgartirilmagan.
- ✅ **Xavfsizlik**: visibility tekshiruvi (private/hidden 404), `is_active`
  tekshiruvi, `is_seller` tekshiruvi.
- ✅ **Tushunarlilik**: barcha yangi qatorlar batafsil izoh bilan.
- ✅ **Hujjatlashtirish**: ushbu fayl + alohida fayl-darajadagi izohlar.
- ✅ **README integrity**: README'ga tegmadik.
