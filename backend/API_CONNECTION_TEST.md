# 🔌 Backend va Frontend Bog'lanishi - Test va Muammolar

## ✅ HOZIRGI HOLAT

### Frontend Configuration:
- **URL:** `http://localhost:5173`
- **Vite Proxy:** `/api/*` → `http://localhost:8000`
- **API Base:** `/api/v1` (relative path - proxy orqali ishlaydi)

### Backend Configuration:
- **URL:** `http://localhost:8000`
- **CORS:** `CORS_ALLOW_ALL_ORIGINS = True` (dev mode)
- **Database:** ⚠️ **SQLite** (db.sqlite3) - PostgreSQL emas!
- **API Docs:** `http://localhost:8000/api/docs/`

---

## ⚠️ MUAMMOLAR

### 1. Database Muammosi
**File:** `backend/config/settings/base.py` (lines 144-149)

```python
# HOZIR - SQLite (not recommended!)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Kerak:** PostgreSQL (commented out, lines 132-143)

**Yechim:** PostgreSQL ishga tushiring va database konfiguratsiyasini o'zgartiring.

### 2. Frontend Hech Qanday API Chaqirmayapti
- Hozir frontend faqat statik sahifa ko'rsatmoqda
- Hech qanday API call yo'q
- Backend bilan bog'lanish test qilinmagan

---

## 🧪 TEST QILISH

### Backend Ishlayotganini Tekshirish:

```bash
# 1. Backend ishga tushirish
cd backend
python manage.py runserver

# 2. Health check
curl http://localhost:8000/healthz
# Expected: {"status": "ok"}

# 3. API docs
# Open browser: http://localhost:8000/api/docs/
```

### Frontend Ishlayotganini Tekshirish:

```bash
# 1. Frontend ishga tushirish
cd frontend
npm run dev

# 2. Open browser
# http://localhost:5173

# 3. Click "Test API Connection" button
```

### Integration Test:

```bash
# 1. Both servers running
# 2. From frontend (http://localhost:5173):
curl http://localhost:5173/healthz
# Should proxy to backend and return: {"status": "ok"}

# 3. Test API endpoint
curl http://localhost:5173/api/v1/auth/register \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "username": "testuser"
  }'
```

---

## 📋 QADAMMA-QADAM YO'L YO'RIQ

### Variant 1: SQLite bilan ishlatish (Tez, lekin production uchun emas)

```bash
# 1. Backend ishga tushirish
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000

# 2. Frontend ishga tushirish (boshqa terminalda)
cd frontend
npm run dev

# 3. Test
# Open: http://localhost:5173
# Click: "Test API Connection"
```

### Variant 2: PostgreSQL bilan ishlatish (Tavsiya etiladi)

```bash
# 1. PostgreSQL ishga tushirish
sudo systemctl start postgresql
sudo -u postgres createdb bittada
sudo -u postgres createuser bittada

# 2. backend/config/settings/base.py ni o'zgartirish:
#    - SQLite blokni comment qilish (lines 144-149)
#    - PostgreSQL blokni uncomment qilish (lines 132-143)

# 3. Backend ishga tushirish
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000

# 4. Frontend ishga tushirish
cd frontend
npm run dev
```

### Variant 3: Docker Compose bilan (Eng yaxshi)

```bash
# 1. Barcha servislarni ishga tushirish
make build
make up
make migrate
make superuser

# 2. Frontend ishga tushirish
make frontend-dev

# 3. Test
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/api/docs/
# Admin:    http://localhost:8000/admin
```

---

## 🔧 MUAMMOLARNI HAL QILISH

### "CORS Error" ko'rsangiz:

Backend `dev.py` da:
```python
CORS_ALLOW_ALL_ORIGINS = True  # Dev mode uchun OK
```

Production da:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://yourdomain.com",
]
```

### "Network Error" yoki "Connection Refused":

1. Backend ishlayotganini tekshiring:
   ```bash
   curl http://localhost:8000/healthz
   ```

2. Vite proxy konfiguratsiyasini tekshiring:
   ```javascript
   // frontend/vite.config.js
   proxy: {
     '/api': { target: 'http://localhost:8000', changeOrigin: true },
   }
   ```

3. Firewall/antivirus tekshiring

### "404 Not Found":

URL to'g'riligini tekshiring:
- ✅ `/api/v1/auth/register`
- ✅ `/api/v1/users/`
- ❌ `/api/auth/register` (v1 yo'q)
- ❌ `/v1/auth/register` (/api yo'q)

---

## 📊 API ENDPOINTS (Hozir Mavjud)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/healthz` | Health check | ✅ Ready |
| GET | `/api/docs/` | Swagger UI | ✅ Ready |
| POST | `/api/v1/auth/register` | Register user | ✅ Ready |
| POST | `/api/v1/auth/login/` | Login (get JWT) | ✅ Ready |
| POST | `/api/v1/auth/otp/request/` | Request OTP | ✅ Ready |
| POST | `/api/v1/auth/otp/confirm/` | Confirm OTP | ✅ Ready |
| GET | `/api/v1/users/me/` | Get current user | ✅ Ready |
| PATCH | `/api/v1/users/me/` | Update profile | ✅ Ready |

---

## 🎯 KEYINGI QADAMLAR

1. ✅ **Database to'g'rilash** - PostgreSQL ga o'tish
2. ✅ **API test qilish** - `/api-test` sahifasidan foydalaning
3. ⏳ **Real frontend features** - P1 catalog pages
4. ⏳ **Authentication flow** - Login/Register UI
5. ⏳ **Product listing** - Catalog page with API data

---

## 📝 ESLATMALAR

- Frontend **relative URL** ishlatadi: `/api/v1/...`
- Vite proxy buni `http://localhost:8000/api/v1/...` ga yo'naltiradi
- Production da `VITE_API_BASE` ni to'liq URL ga o'zgartiring
- Hozir P0 phase - faqat foundation tayyor
- Real features P1 da keladi (catalog, products, etc.)
