# Bittada ERP — Alohida boshqaruv ekotizimi (2026-05-02 v3)

> **Strategik maqsad:** Bittada ERP boshqaruv tizimi Django'ning standart admin panelidan **butunlay ajratiladi**. Bu — alohida URL prefiksi, alohida API qatlami, custom ViewSet'lar, alohida middleware bilan qurilgan **mustaqil ekotizim**. Shu orqali sayt foydalanuvchilari va sotuvchilar Django'ning quruq formasini hech qachon ko'rmaydi.

---

## 🎯 Arxitektura uchligi

| Dunyo | URL prefiksi | Maqsadi | Foydalanuvchilar |
|-------|--------------|---------|------------------|
| **Saytning ochiq qismi** | `/`, `/shop/`, `/services/`, `/login/` | B2C/B2B mehmonlar va sayt | Hammaga ochiq |
| **Bittada ERP boshqaruv** | `/dashboard/` (HTML) + `/dashboard/api/v1/` (DRF) | Sales/Escrow/Credit/Users boshqaruvi | Seller, Admin, Super Admin |
| **Django Core DB** | `/hidden-core-database/` | DB darajasidagi tekshirish (maxfiy) | Faqat tizim ma'muri |

---

## 📁 Yangi yaratilgan ilova: `apps/management/`

13 ta yangi fayl + 6 ta yangi template:

```
apps/management/
├── __init__.py                  # Modul docstring (ekotizim haqida)
├── apps.py                      # ManagementConfig (AppConfig)
├── permissions.py               # IsManagementUser, IsManagementAdmin, MANAGEMENT_ROLES
├── middleware.py                # ManagementAccessMiddleware (Firewall)
├── selectors.py                 # Read-only querylar (Products/Orders/Escrow/Users/Credit)
├── services.py                  # Write operatsiyalari (transactional)
├── views.py                     # 6 ta Django Template View (HTML render)
├── urls.py                      # /dashboard/* HTML routes
├── api_urls.py                  # /dashboard/api/v1/* DRF routes (DefaultRouter)
├── api/
│   ├── __init__.py
│   ├── serializers.py           # ManagementProduct/Order/UserSerializer
│   └── viewsets.py              # 5 ta ModelViewSet
└── tests/__init__.py            # Pytest moduli (testlar keyingi vazifada)

templates/management/
├── products_list.html           # To'liq ERP UI (KPI, jadval, JS bilan AJAX yangilash)
├── orders_list.html             # Skeleton + 5 ta KPI + jadval
├── escrow_list.html             # Skeleton + 4 ta KPI + frozen orders
├── credit_list.html             # Placeholder (apps.billing keyingi vazifada)
├── users_list.html              # Skeleton + 4 ta KPI + jadval
└── blacklist_list.html          # Bloklangan foydalanuvchilar
```

---

## 🛡️ ManagementAccessMiddleware — "Firewall"

[apps/management/middleware.py](../../backend/apps/management/middleware.py)

```python
# Mantiq:
# 1. /dashboard/ bilan boshlanmasa → o'tkazib yuborish
# 2. Anonim foydalanuvchi:
#    - HTML so'rov → 302 → /login/?next=<path>
#    - JSON so'rov → 401 {"detail": "Authentication required.", "code": "not_authenticated"}
# 3. Autentifikatsiyalangan, lekin ruxsati yo'q (customer):
#    - HTML → 302 → /login/?error=no_access&next=<path>
#    - JSON → 403 {"detail": "Sizda...", "code": "permission_denied"}
# 4. is_staff/is_superuser/role IN (seller,admin,super_admin) → o'tkazadi
```

**MIDDLEWARE'da joylashuvi:** `AuthenticationMiddleware`'dan keyin (chunki `request.user`'ga ehtiyoji bor).

---

## 🔑 Permissions (3 darajali himoya)

[apps/management/permissions.py](../../backend/apps/management/permissions.py)

| Permission | Kim kira oladi | Foydalanish |
|------------|----------------|-------------|
| `is_management_user(user)` | Yagona haqiqat manbai (helper) | Middleware + view'lar |
| `IsManagementUser` (DRF) | Seller/Admin/SuperAdmin/staff | Products, Orders, Escrow, Credit ViewSets |
| `IsManagementAdmin` (DRF) | Faqat Admin/SuperAdmin/staff (Seller emas) | Users ViewSet (bloklash) |

`MANAGEMENT_ROLES = {"seller", "admin", "super_admin"}` — yagona konstanta.

---

## 🌐 DRF API qatlami — `/dashboard/api/v1/`

[apps/management/api_urls.py](../../backend/apps/management/api_urls.py) → `DefaultRouter` orqali avtomatik:

| ViewSet | URL | Endpointlar |
|---------|-----|-------------|
| `ManagementProductViewSet` | `/products/` | List/Create/Retrieve/Update/Delete + `/kpis/` |
| `ManagementOrderViewSet` | `/orders/` | List/Retrieve/Update + `/kpis/` |
| `ManagementEscrowViewSet` | `/escrow/` | List/Retrieve + `/kpis/` |
| `ManagementUserViewSet` | `/users/` | List/Retrieve/Update + `/block/`, `/unblock/`, `/blacklist/`, `/kpis/` |
| `ManagementCreditViewSet` | `/credit/` | List + `/kpis/` |

**Filterlash, qidiruv, saralash:** `?search=...&ordering=-created_at&...` (DRF SearchFilter + OrderingFilter).

**Rolga ko'ra filterlash:** Selectors qatlamida (`list_products_for_management(user)` — Seller faqat o'zinikilarni ko'radi, Admin hammasini).

---

## 📁 O'zgartirilgan fayllar (mavjudlar)

### 1. [backend/config/settings/base.py](../../backend/config/settings/base.py)
- `INSTALLED_APPS`: `+ "apps.management"`
- `MIDDLEWARE`: `+ "apps.management.middleware.ManagementAccessMiddleware"` (Auth'dan keyin)

### 2. [backend/config/urls.py](../../backend/config/urls.py)
- `super-admin/` → **`hidden-core-database/`** (yana ko'chirildi, foydalanuvchi talabiga ko'ra)
- `+ path("dashboard/api/v1/", include("apps.management.api_urls"))` (API qatlam)
- `+ path("dashboard/", include(("apps.management.urls", "management"), namespace="mgmt"))`
- `hidden-core-database/login/` → RedirectView('/login/') — Django admin login formasi ko'rinmaydi
- `api_root` JSON: yangi endpoint'lar haqida ma'lumot (`erp_dashboard`, `erp_api`, `django_admin_db`)

### 3. [backend/templates/includes/erp_sidebar.html](../../backend/templates/includes/erp_sidebar.html)
- Barcha linklar yangilandi:
  - Savdo → `{% url 'mgmt:orders_list' %}`
  - Mahsulotlar → `{% url 'mgmt:products_list' %}`
  - Escrow Fund → `{% url 'mgmt:escrow_list' %}`
  - Credit Economy → `{% url 'mgmt:credit_list' %}`
  - Foydalanuvchilar → `{% url 'mgmt:users_list' %}`
  - Qora ro'yxat → `{% url 'mgmt:blacklist' %}`
  - Django Admin → `/hidden-core-database/` (System bo'limida, target=_blank)
- `active` holat marker'lari yangilandi (`/dashboard/products` va h.k.)

### 4. [backend/templates/includes/erp_navbar.html](../../backend/templates/includes/erp_navbar.html)
- Command Center → `{% url 'mgmt:index' %}` (ya'ni `/dashboard/`)

### 5. [backend/apps/products/urls.py](../../backend/apps/products/urls.py)
- Eski `manage/products/` URL'lari **RedirectView** ga aylantirildi:
  - `manage/products/` → `/dashboard/products/`
  - `manage/products/create/` → `/dashboard/products/`
- `name='admin_product_list'` saqlandi → eski template'lardagi `{% url %}` chaqiruvlari NoReverseMatch bermaydi

### 6. [backend/apps/products/views.py](../../backend/apps/products/views.py)
- **TEGILMADI** — `product_admin_list_view`, `product_admin_create_view`, `_is_panel_user` mavjud, lekin endi `apps.management.views` ga ko'chdi (logikan)
- Eski view funksiyalari saqlandi (daxlsizlik kafolati)

---

## 🧪 Tekshirilgan oqimlar (HTTP test matritsasi)

```
═══ ANONIM FOYDALANUVCHI ═══
GET  /dashboard/                 → 302 → /login/?next=/dashboard/             ✅
GET  /dashboard/products/        → 302 → /login/?next=/dashboard/products/    ✅
GET  /dashboard/api/v1/products/ → 401 {"code": "not_authenticated"}           ✅

═══ AUTENTIFIKATSIYALANGAN SUPERUSER ═══
GET  /dashboard/                 → 302 → /dashboard/products/                 ✅
GET  /dashboard/products/        → 200 (HTML, KPI, jadval)                    ✅
GET  /dashboard/orders/          → 200                                        ✅
GET  /dashboard/escrow/          → 200                                        ✅
GET  /dashboard/credit/          → 200                                        ✅
GET  /dashboard/users/           → 200 (admin OK)                             ✅
GET  /dashboard/users/blacklist/ → 200                                        ✅

═══ DRF API ═══
GET  /dashboard/api/v1/products/      → 200 [{...}, ...]                      ✅
GET  /dashboard/api/v1/products/kpis/ → {"total":2,"published":0,"draft":2}   ✅
GET  /dashboard/api/v1/orders/kpis/   → {"total_orders":0,...,"gmv":0.0}      ✅
GET  /dashboard/api/v1/escrow/kpis/   → {"frozen_total":0.0,...}              ✅
GET  /dashboard/api/v1/users/kpis/    → {"total":6,"customers":0,"sellers":3} ✅
GET  /dashboard/api/v1/credit/        → {"kpis": {...}, "transactions": []}   ✅

═══ DJANGO ADMIN (MAXFIY) ═══
GET  /hidden-core-database/login/  → 302 → /login/                            ✅
GET  /admin/  (eski)               → 404                                       ✅
GET  /super-admin/ (eski)          → 404                                       ✅

═══ ESKI URL'LAR ═══
GET  /manage/products/         → 302 → /dashboard/products/                   ✅
GET  /manage/products/create/  → 302 → /dashboard/products/                   ✅

═══ SAYT (avvalgi, tegilmagan) ═══
GET  /          → 200  ✅
GET  /login/    → 200  ✅
GET  /services/ → 200  ✅
```

`manage.py check` → 0 ta xato.

---

## 🐛 Topilgan va tuzatilgan bug

**Bug:** `User.objects.order_by("-date_joined")` → `FieldError`. Loyiha User modeli `BaseModel` dan `created_at`'ni meros qiladi, `date_joined` yo'q.

**Tuzatish:** Selectors, viewsets, va template'lardagi `date_joined` → `created_at`.

---

## 🛡️ Daxlsizlik kafolati (Loyiha qoidasi 1)

Hech qanday mavjud kod buzilmadi:
- ✅ `apps/products/views.py` — TEGILMADI (eski view funksiyalari saqlandi)
- ✅ `apps/products/admin.py` — TEGILMADI (Django admin ishlashda davom etadi, faqat URL ko'chdi)
- ✅ `apps/orders/models.py`, `apps/users/models.py` — TEGILMADI
- ✅ `apps/dashboard/` (eski API ilova) — TEGILMADI (alohida API'da ishlayotganda davom etadi)
- ✅ Sayt URL'lari (`/`, `/login/`, `/services/`, `/shop/`) — ishlayapti
- ✅ Mavjud `{% url 'home' %}`, `{% url 'logout' %}`, `{% url 'profile' %}` linklari — saqlandi

---

## 📝 Hujjatlashtirish (Loyiha qoidasi 4)

- ✅ Bu hisobot fayli (~250 qator)
- ✅ Har bir yangi fayl boshida modul docstring'i (maqsad, tarkib, foydalanish)
- ✅ Har bir funksiya/klass docstring bilan
- ✅ Har bir kod qatorida izoh (Loyiha qoidasi 2 — tushunarlilik)

---

## 🚀 Keyingi qadamlar (kelajak vazifalar)

1. **Mahsulotlar to'liq UI** — modal-based create/edit forma, image upload, drag-and-drop
2. **Orders to'liq UI** — status o'zgartirish (escrow release/refund), conversation thread
3. **Escrow operatsiyalari** — apps.escrow.services bilan integratsiya (release/refund/dispute)
4. **Credit Economy** — apps.billing modeli to'liq amalga oshganda transaction history, balanslar
5. **Users boshqaruv to'liq UI** — block/unblock tugmalari, rol o'zgartirish, KYC tasdiqlash
6. **Pagination** — DRF DefaultPagination ulanishi (25 → "load more")
7. **WebSocket** — real-time KPI yangilanishi (apps.notifications bilan integratsiya)
8. **Tests** — pytest test'lar (`apps/management/tests/`) — permissions, middleware, viewsets

---

## 🔗 URL xaritasi (yakuniy)

```
GLOBAL
├── /                              # Bosh sahifa (sayt)
├── /login/                        # ERP login (yagona kirish nuqtasi)
├── /logout/                       # Logout
├── /shop/, /services/, /cart/...  # Sayt sahifalari
│
├── /api/v1/...                    # Public sayt API (auth, products, orders)
├── /api/docs/                     # Swagger UI
├── /api/schema/                   # OpenAPI sxema
│
├── /dashboard/                    # ⭐ Bittada ERP — bosh sahifa
│   ├── /products/                 # Mahsulotlar (to'liq UI)
│   ├── /orders/                   # Savdo (skeleton)
│   ├── /escrow/                   # Escrow Fund (skeleton)
│   ├── /credit/                   # Credit Economy (placeholder)
│   ├── /users/                    # Foydalanuvchilar (admin only, skeleton)
│   ├── /users/blacklist/          # Qora ro'yxat (admin only)
│   │
│   └── /api/v1/                   # ⭐ ERP DRF API
│       ├── /products/             # Products CRUD + /kpis/
│       ├── /orders/               # Orders + /kpis/
│       ├── /escrow/               # Escrow read-only + /kpis/
│       ├── /users/                # Users + /block/, /unblock/, /blacklist/, /kpis/
│       └── /credit/               # Credit + /kpis/
│
└── /hidden-core-database/         # ⭐ Django admin (maxfiy, DB tekshirish uchun)
    ├── /login/                    # → /login/ ga redirect
    ├── /logout/                   # → /logout/ ga redirect
    └── /<model>/<pk>/...          # Standart Django admin operatsiyalari
```
