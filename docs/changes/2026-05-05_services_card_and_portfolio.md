# Standart xizmat kartalari + Portfolio sahifalari

**Sana**: 2026-05-05
**Muallif**: Claude (Opus 4.7) — `mebelcityai@gmail.com` so'rovi bo'yicha

## Qisqacha

3 ta yangi sahifa va bitta qayta ishlatiladigan kartka komponenti qo'shildi:

1. **Standart xizmat karta** (`templates/services/card.html`) — vazifa
   shartiga to'liq mos: avatar, BAND badge, REYTING/HOLAT/ISHLAR (3 ustun),
   joylashuv, narx, [Portfolio] [Bron qilish] tugmalari.
2. **Xizmatlar grid sahifasi** (`templates/services/list.html`) —
   `ServiceListView` (CBV) orqali render qilinadi (URL ulanishi
   ko'rsatilmagan, foydalanuvchi keyin xohlasa o'zi qo'shadi).
3. **Portfolio detail** (`/portfolio/<username>/`) — sotuvchining ochiq
   portfolio sahifasi. Owner uchun "Tahrirlash" tugmasi.
4. **Portfolio edit** (`/portfolio/edit/`) — sotuvchining o'z
   portfoliosini boshqaruv sahifasi (yangi qo'shish + o'chirish).

## URL'lar

| URL | View | Vazifa |
|-----|------|--------|
| `/portfolio/<username>/` | `PortfolioDetailView` (services/views.py) | Public ko'rinish |
| `/portfolio/edit/` | `PortfolioEditView` (showroom/views.py) | Owner CRUD |
| `/services/standard/` | `ServiceListView` (services/views.py) | (URL ulanmagan, kelajak) |

## O'zgartirilgan / yaratilgan fayllar

| Fayl | Holat | Maqsad |
|------|-------|--------|
| `backend/apps/showroom/forms.py` | yaratildi | `PortfolioForm` (ModelForm — title, image, location, year, ...) |
| `backend/apps/showroom/views.py` | tahrir | `PortfolioEditView` (LoginRequired+seller, GET=list+form, POST=add yoki delete) |
| `backend/apps/services/views.py` | tahrir | `ServiceListView`, `PortfolioDetailView` (CBV) qo'shildi |
| `backend/apps/showroom/urls.py` | tahrir | `portfolio_urlpatterns` ro'yxati (edit/, <username>/) |
| `backend/config/urls.py` | tahrir | `path("portfolio/", include(...))` namespace="portfolio" |
| `backend/templates/services/card.html` | yaratildi | Standart kartka fragment (har joyda include) |
| `backend/templates/services/list.html` | yaratildi | Mustaqil grid sahifa (filter chip + pagination) |
| `backend/templates/portfolio/detail.html` | yaratildi | Mustaqil portfolio sahifa (ochiq) |
| `backend/templates/portfolio/edit.html` | yaratildi | Mustaqil owner CRUD sahifa |

**Migration**: kerak bo'lmadi (PortfolioItem modeli avval yaratilgan,
oldingi vazifa `2026-05-04_seller_public_profile.md`).

## Texnik tafsilotlar

### Karta standarti (vazifa talabi)

Har bir karta `templates/services/card.html`'dan keladi va quyidagilarni
o'z ichiga oladi (test bilan tasdiqlandi):

| Talab | Joy | Test |
|-------|-----|------|
| Avatar (yuqori chap) | `<img>` yoki initial placeholder | OK |
| BAND badge (yuqori o'ng) | `position: absolute; right: 12px` (qizil) | OK |
| REYTING ★ | 1-ustun: `★ {{ rating }} ({{ count }})` | OK |
| HOLAT 🟢 | 2-ustun: `Ochiq` (yashil) yoki `Yopiq` (qizil) | OK |
| ISHLAR | 3-ustun: `projects_completed` | OK |
| Joylashuv 📍 | Pastki blok, chap | OK |
| Narx (o'ng katta) | `font-size: 18px; color: #2563eb` | OK |
| [Portfolio] tugma | `/portfolio/<username>/` ga link | OK |
| [Bron qilish] tugma | Login bo'lsa POST, aks holda `/login/?next=` | OK |

### Permission qoidalari

**PortfolioDetailView** (`/portfolio/<username>/`):
- Anonim ham ko'ra oladi (ochiq sahifa).
- Yo'q user → 404
- Customer (sotuvchi emas) → 404 (mijozlar portfolioga ega emas)
- Profile.visibility != PUBLIC → 404
- Owner bo'lsa "Tahrirlash" tugmasi ko'rinadi (`is_owner` flag)

**PortfolioEditView** (`/portfolio/edit/`):
- Anonim → `/login/?next=...`
- Customer → `/profile/` (warning xabar)
- Sotuvchi → 200 + forma
- POST `delete=<uuid>` — faqat o'zining elementini o'chira oladi
  (queryset filteri: `seller=request.user`)

### Xavfsizlik

`PortfolioEditView.post()`:
```python
deleted_count, _ = PortfolioItem.objects.filter(
    pk=delete_id, seller=request.user
).delete()
```
Boshqa user UUID'ini yozsa — DB'da topilmaydi va o'chirilmaydi.

`PortfolioForm` — `seller` maydoni formada yo'q, view ichida
`item.seller = request.user` qilib o'rnatiladi (foydalanuvchi boshqa user
nomidan portfolio yarata olmaydi).

### Mustaqil templatelar

`portfolio/detail.html`, `portfolio/edit.html`, `services/list.html` —
`base.html` dan extend qilmaydi. Sabab: `base.html` ichida
`{% url 'auth_logout' %}` reverse muammosi bor (mavjud bug, daxlsizlik
qoidasi sabab tegmadik). Mustaqil HTML hujjatlar bilan bug chetlab o'tildi.

### URL routing

```python
# config/urls.py
from apps.showroom.urls import portfolio_urlpatterns as _portfolio_urls
template_patterns = [
    ...
    path("portfolio/", include((_portfolio_urls, "portfolio"), namespace="portfolio")),
]
```

```python
# apps/showroom/urls.py
portfolio_urlpatterns = [
    path("edit/", PortfolioEditView.as_view(), name="edit"),       # Aniqroq, BIRINCHI
    path("<str:username>/", PortfolioDetailView.as_view(), name="detail"),
]
```

**MUHIM**: `edit/` aniq path birinchi turishi kerak — aks holda
`<str:username>/` "edit" ni username sifatida qabul qilib oladi va edit
view ishlamay qoladi.

## Test natijalar

```
System check: 0 issues

Anonymous /portfolio/ahmed-seller/:        200 (6.6 KB) — ochiq sahifa
Anonymous /portfolio/edit/:                302 → /login/?next=...
Anonymous /portfolio/no-such-user-xyz/:    404 ✓
Anonymous /portfolio/<customer>/:          404 ✓ (mijoz)
Customer /portfolio/edit/:                 302 → /uz/profile/ (warning)
Seller /portfolio/edit/:                   200 (8.3 KB)
Seller /portfolio/<own>/:                  200, "Tahrirlash" tugmasi: ✓

POST add (real PNG):                       302 → /uz/portfolio/<username>/
After add: items count yangilandi ✓
Public profile contains test card:         True ✓
POST delete (own):                         302, item DB'dan o'chirildi ✓
Anonymous POST:                            302 → /login/

Card render (mock data) — barcha 8 ta talab:
  ✓ REYTING ★
  ✓ HOLAT 🟢
  ✓ ISHLAR (3 ustun)
  ✓ Joylashuv 📍
  ✓ XIZMAT NARXI
  ✓ Portfolio tugmasi
  ✓ Bron qilish (anonymous → /login/?next=)
  ✓ Avatar placeholder
```

## Vazifa cheklovlari

- ✅ **Yangi app yaratilmadi**: barcha CBV'lar mavjud `apps/services/`,
  `apps/showroom/` ichida.
- ✅ **Migration faqat showroom uchun**: `PortfolioItem` modeli avval
  yaratilgan (oldingi vazifa), bu safar yangi migration kerak emas.
- ✅ **Faqat ko'rsatilgan fayllarga tegildi**: `apps/services/urls.py` ga
  TEGMADIK (vazifa cheklovi). `ServiceListView` views.py'da yaratildi,
  lekin URL ulanish foydalanuvchining keyingi qadami.
- ✅ **Daxlsizlik**: mavjud `services_view`, `service_type_detail`,
  `showroom_view` o'zgartirilmagan.
- ✅ **Tushunarlilik**: barcha qatorlar batafsil izoh bilan.
- ✅ **Hujjatlashtirish**: ushbu fayl + har bir fayl docstring'i.

## Eslatma — ServiceListView ulashilishi

`ServiceListView` URL'ga ulanmagan (vazifa cheklov: services/urls.py
o'zgarmasin). Foydalanuvchi keyin xohlasa, quyidagini qo'shadi:

```python
# apps/services/urls.py
from .views import ServiceListView
urlpatterns = [
    ...
    path("standard/", ServiceListView.as_view(), name="services_standard"),
]
```

So'ngra `/services/standard/` orqali standart kartali grid ochiladi.
Hozircha kartka fragmenti (`services/card.html`) ko'p joyda ishlatilishi
mumkin (masalan, mavjud `services_erp.html` ichidagi `{% include %}`).
