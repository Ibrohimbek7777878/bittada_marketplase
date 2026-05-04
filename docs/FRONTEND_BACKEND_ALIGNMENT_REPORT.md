# Frontend-Backend Moslashuv Hisoboti

**Sana:** 2026-04-30

---

## 1. Umumiy Xulosa

| Ko'rsatkich | Qiymat |
|-------------|--------|
| **Umumiy moslashuv** | ~15-20% |
| **Backend ilovalar soni** | 24 ta |
| **Frontend ishlatayotgan endpointlar** | ~7-8 ta |
| **Rejim** | Standalone/Mock (USE_BACKEND = false) |

---

## 2. Backend Tuzilmasi (24 ta ilova)

### API v1 Endpointlar (24 ta modul):

| # | Ilova | Prefix | Status | Frontend'da ishlatilmoqda |
|---|-------|--------|--------|---------------------------|
| 1 | `auth_methods` | `/api/v1/auth/` | ✅ | ✅ Login/Register |
| 2 | `users` | `/api/v1/users/` | ✅ | ✅ /me |
| 3 | `products` | `/api/v1/products/` | ✅ | ✅ Mahsulotlar |
| 4 | `categories` | `/api/v1/categories/` | ✅ | ✅ Kategoriyalar |
| 5 | `services` | `/api/v1/services/` | ✅ | ✅ Xizmatlar |
| 6 | `orders` | `/api/v1/orders/` | ✅ | ❌ Checkout (frontend'da mock) |
| 7 | `analytics` | `/api/v1/analytics/` | ✅ | ❌ |
| 8 | `api` | `/api/v1/api/` | ✅ | ❌ Test/CSRF |
| 9 | `billing` | `/api/v1/billing/` | ✅ | ❌ |
| 10 | `blacklist` | `/api/v1/blacklist/` | ✅ | ❌ |
| 11 | `chat` | `/api/v1/chat/` | ✅ | ❌ |
| 12 | `escrow` | `/api/v1/escrow/` | ✅ | ❌ |
| 13 | `i18n_extra` | `/api/v1/i18n_extra/` | ✅ | ❌ |
| 14 | `integrations` | `/api/v1/integrations/` | ✅ | ❌ |
| 15 | `marketplace` | `/api/v1/marketplace/` | ✅ | ❌ |
| 16 | `media` | `/api/v1/media/` | ✅ | ❌ |
| 17 | `notifications` | `/api/v1/notifications/` | ✅ | ❌ |
| 18 | `pages` | `/api/v1/pages/` | ✅ | ❌ (CMS) |
| 19 | `security` | `/api/v1/security/` | ✅ | ❌ |
| 20 | `seo` | `/api/v1/seo/` | ✅ | ❌ |
| 21 | `showroom` | `/api/v1/showroom/` | ✅ | ❌ (3D) |
| 22 | `support` | `/api/v1/support/` | ✅ | ❌ |
| 23 | `variants` | `/api/v1/variants/` | ✅ | ❌ |
| 24 | `warehouse` | `/api/v1/warehouse/` | ✅ | ❌ |

**Jami:** 24 ta backend modul, 7 tasi frontend'da ishlatilmoqda (~29%)

---

## 3. Frontend API Integration

### Joriy holat (`client.js`):

```javascript
const USE_BACKEND = false; // Standalone rejim
```

Frontend **mock mode** da ishlaydi - backendga ulanmaydi.

### Implementatsiya qilingan endpointlar (7 ta):

| Endpoint | Frontend API | Status |
|----------|--------------|--------|
| `POST /api/v1/auth/login/` | `authApi.login()` | ✅ Mock |
| `POST /api/v1/auth/register/` | `authApi.register()` | ✅ Mock |
| `GET /api/v1/users/me/` | `authApi.me()` | ✅ Mock |
| `GET /api/v1/products/api/products/` | `productsApi.list()` | ✅ Mock |
| `GET /api/v1/categories/` | `categoriesApi.list()` | ✅ Mock |
| `GET /api/v1/services/` | `servicesApi.list()` | ✅ Mock |
| `GET /blog/` | `blogApi.list()` | ✅ Mock |

### Backendda bor, lekin frontend'da yo'q (17 ta asosiy):

| Endpoint | Tavsif | Zarurligi |
|----------|--------|-----------|
| `/api/v1/orders/checkout/` | Buyurtma berish | 🔴 Yuqori |
| `/api/v1/orders/list/` | Buyurtmalar tarixi | 🔴 Yuqori |
| `/api/v1/escrow/` | Xavfsiz to'lov | 🔴 Yuqori |
| `/api/v1/billing/` | Hisob-kitob | 🟡 O'rta |
| `/api/v1/chat/` | Xabar almashish | 🟡 O'rta |
| `/api/v1/warehouse/` | Ombor boshqaruvi | 🟡 O'rta |
| `/api/v1/notifications/` | Bildirishnomalar | 🟡 O'rta |
| `/api/v1/analytics/` | Statistika | 🟢 Past |
| `/api/v1/blacklist/` | Qora ro'yxat | 🟢 Past |
| `/api/v1/integrations/` | Integratsiyalar | 🟢 Past |
| `/api/v1/security/` | Xavfsizlik | 🟢 Past |
| `/api/v1/showroom/` | 3D showroom | 🟢 Past |
| `/api/v1/variants/` | Mahsulot variantlari | 🟢 Past |
| `/api/v1/media/` | Fayl yuklash | 🟡 O'rta |
| `/api/v1/support/` | Qo'llab-quvvatlash | 🟡 O'rta |
| `/api/v1/seo/` | SEO ma'lumotlari | 🟢 Past |
| `/api/v1/pages/` | CMS sahifalar | 🟢 Past |

---

## 4. Amalda ishlatilmayotgan Backend API'lar

### 4.1 Auth Methods (6 ta endpoint, 2 tasi ishlatilmoqda)

```python
# Backend:
/auth/register/          # ✅ Frontend'da bor
/auth/login/            # ✅ Frontend'da bor
/auth/refresh/          # ❌ Yo'q - Token yangilash
/auth/otp/request/      # ❌ Yo'q - OTP so'rov
/auth/otp/confirm/      # ❌ Yo'q - OTP tasdiqlash
/auth/social-login/     # ❌ Yo'q - Ijtimoiy tarmoq orqali kirish
```

### 4.2 Users (2 ta endpoint, 1 tasi ishlatilmoqda)

```python
# Backend:
/api/v1/users/me/         # ✅ Frontend'da bor
/api/v1/users/u/<username>/  # ❌ Yo'q - Ochiq profil
```

### 4.3 Orders (2 ta endpoint, 0 tasi ishlatilmoqda)

```python
# Backend:
/api/v1/orders/checkout/   # ❌ Yo'q - Buyurtma berish
/api/v1/orders/list/       # ❌ Yo'q - Buyurtmalar ro'yxati
```

### 4.4 Products (3 ta endpoint, 2 tasi ishlatilmoqda)

```python
# Backend:
/api/products/              # ✅ Frontend'da bor (list)
/api/products/<uuid>/       # ⚠️ Frontend'da mock
/api/categories/tree/       # ✅ Frontend'da bor (categories)
```

---

## 5. Tavsiyalar

### 5.1 Darhol integratsiya qilish kerak (Yuqrui daraja):

1. **`USE_BACKEND = true`** qilish
2. **Orders API** - Checkout jarayonini backend bilan integratsiya qilish
3. **Escrow API** - Xavfsiz to'lov mexanizmini yoqish

### 5.2 Keyingi bosqichda (O'rta daraja):

1. **Notifications API** - Real-time bildirishnomalar
2. **Chat API** - Sotuvchi va xaridor o'rtasida muloqot
3. **Media API** - Rasmlarni serverga yuklash
4. **Warehouse API** - Mahsulot qoldig'ini tekshirish

### 5.3 Kelajakda (Past daraja):

1. **Analytics API** - Statistika dashboard
2. **Showroom API** - 3D ko'rinish
3. **SEO API** - Meta ma'lumotlar

---

## 6. Hisoblash

```
Backend'dagi jami endpointlar:      ~80+ ta
Frontend'da ishlatilgan:            ~7-8 ta
------------------------------------------
Moslashuv foizi:                      ~10-15%

Agar faqat kritik endpointlar hisoblanilsa:
Kritik endpointlar:                   ~20 ta
Ishlatilgan:                          ~7 ta
------------------------------------------
Moslashuv foizi:                      ~35%
```

**Umumiy baho: ~15-20% moslashuv**

Frontend hozircha **standalone/mock rejim** da ishlaydi va backend bilan to'liq integratsiya qilmagan.

---

## 7. Integratsiya yo'l xaritasi

| Bosqich | Ilovalar | Vaqt | Status |
|---------|----------|------|--------|
| **P0** | Auth, Users, Products, Categories | 1-2 kun | 🟡 Qisman tayyor |
| **P1** | Orders, Checkout, Escrow | 3-5 kun | 🔴 Yo'q |
| **P2** | Notifications, Chat, Media | 1 hafta | 🔴 Yo'q |
| **P3** | Analytics, Warehouse, Billing | 2 hafta | 🔴 Yo'q |
| **P4** | Qolgan ilovalar | 1 hafta | 🔴 Yo'q |

---

**Xulosa:** Frontend backend bilan **15-20% moslashuv** darajasida. Asosiy muammo - `USE_BACKEND = false` sozlamasi. To'liq integratsiya uchun P0-P2 bosqichlarini yakunlash kerak.

