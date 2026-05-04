# 🚀 Bitta Portda Backend va Frontend Ishlatish

## ✅ Tayyor!

Backend va frontend endi **BITTA PORTDA** (8000) ishlaydi!

---

## 🎯 Qanday Ishlatish

### **Variant 1: Start Script (Eng Oson)**

```bash
cd /home/ibrohim/Desktop/client_baza/bittada_market_ekosistema

# Hammasini avtomatik ishga tushirish
./start.sh
```

Script avtomatik:
1. ✅ Frontend build qiladi (agar kerak bo'lsa)
2. ✅ Database migrate qiladi
3. ✅ Superuser tekshiradi
4. ✅ Django serverni 8000 portda ishga tushiradi

### **Variant 2: Qo'lda Ishga Tushirish**

```bash
# 1. Frontend build qilish
cd frontend
npm install
npm run build
cd ..

# 2. Database migrate qilish
cd backend
python manage.py migrate

# 3. Django server ishga tushirish (frontend bilan birga!)
python manage.py runserver 8000
```

---

## 🌐 Ishlaydigan URLlar

Barchasi **BITTA PORTDA** (8000):

| Xizmat | URL | Tavsif |
|--------|-----|--------|
| 🎨 **Frontend** | `http://localhost:8000/` | Vite-built SPA |
| 🔌 **API** | `http://localhost:8000/api/v1/` | REST API |
| 📚 **API Docs** | `http://localhost:8000/api/docs/` | Swagger UI |
| ⚙️ **Admin** | `http://localhost:8000/admin/` | Django Admin |
| 💚 **Health** | `http://localhost:8000/healthz` | Health check |
| 📊 **Schema** | `http://localhost:8000/api/schema/` | OpenAPI schema |

---

## 🧪 Test Qilish

### **1. Frontend Test:**

Browser oching: `http://localhost:8000`

"🔌 Test API Connection" tugmasini bosing.

**Kutilayotgan natija:**
```
✅ Backend API is fully connected!
Timestamp: 2026-04-27T15:30:00+05:00
Database: connected | Cache: not_configured
```

### **2. API Test (Terminal):**

```bash
# Health check
curl http://localhost:8000/healthz
# Response: {"status": "ok"}

# API test endpoint
curl http://localhost:8000/api/v1/api/test-connection/
# Response: {"status": "ok", "message": "Backend API is fully connected!", ...}

# API docs (browser)
# http://localhost:8000/api/docs/
```

### **3. User Registration Test:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "username": "testuser"
  }'
```

---

## 📊 Arxitektura - Qanday Ishlaydi

```
┌──────────────────────────────────────────┐
│  Django Server (http://localhost:8000)   │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  URL Routing                       │  │
│  │                                    │  │
│  │  /api/*        → DRF ViewSets     │  │
│  │  /admin/*      → Django Admin     │  │
│  │  /static/*     → Static Files     │  │
│  │  /media/*      → Media Files      │  │
│  │  /*            → Frontend SPA     │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  Frontend (Built by Vite)          │  │
│  │  frontend/dist/index.html         │  │
│  │  frontend/dist/assets/*.js        │  │
│  │  frontend/dist/assets/*.css       │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

### Request Flow:

```
User Request: http://localhost:8000/
    ↓
Django URL Router
    ↓
Is it /api/*?     → YES → API Handler (DRF)
Is it /admin/*?   → YES → Django Admin
Is it /static/*?  → YES → Static Files
Is it /healthz?   → YES → Health Check
Anything else?    → YES → Serve frontend/index.html (SPA)
```

---

## ⚙️ Configuration

### **Development Mode (DEBUG=True):**

Default: Frontend **alohida** Vite serverda ishlaydi (`localhost:5173`)

Agar Django'dan serve qilishni xohlasangiz:

```bash
# .env faylida
DJANGO_SERVE_FRONTEND=1

# Yoki environment variable
export DJANGO_SERVE_FRONTEND=1

# Keyin ishga tushiring
cd backend
python manage.py runserver 8000
```

### **Production Mode (DEBUG=False):**

Frontend **avtomatik** Django'dan serve qilinadi.

```bash
# 1. Frontend build
cd frontend && npm run build

# 2. Django run
cd backend
python manage.py runserver 8000
```

---

## 🔄 Development Workflow

### **Development (Hot Reload bilan):**

Agar sizga hot reload kerak bo'lsa (frontend o'zgarishlarini darhol ko'rish):

**Terminal 1 - Backend:**
```bash
cd backend
python manage.py runserver 8000
```

**Terminal 2 - Frontend (Hot Reload):**
```bash
cd frontend
npm run dev
```

**Keyin:** `http://localhost:5173` ni oching

### **Production (Bitta Port):**

```bash
./start.sh
```

**Keyin:** `http://localhost:8000` ni oching

---

## 📁 O'zgartirilgan Fayllar

1. ✅ `backend/config/settings/base.py`
   - `FRONTEND_DIST` qo'shildi
   - `STATICFILES_DIRS` yangilandi

2. ✅ `backend/config/settings/dev.py`
   - `SERVE_FRONTEND_IN_DEV` flag qo'shildi

3. ✅ `backend/config/urls.py`
   - Frontend catch-all routes qo'shildi

4. ✅ `backend/apps/pages/views.py`
   - `serve_frontend()` view yaratildi

5. ✅ `frontend/dist/`
   - Vite build output

6. ✅ `start.sh`
   - Automated startup script

---

## 🎨 Frontend Yangilash

Frontend kodini o'zgartirgandan keyin:

```bash
# Build qilish
cd frontend
npm run build

# Django avtomatik yangi fayllarni serve qiladi
# Serverni qayta ishga tushirish SHART EMAS!
```

---

## ⚠️ Muhim Eslatmalar

1. **Frontend Build:**
   - Production mode da frontend build qilingan bo'lishi kerak
   - Agar `frontend/dist/index.html` bo'lmasa, 503 error ko'rasiz

2. **Static Files:**
   - `python manage.py collectstatic` production da kerak
   - Dev mode da kerak emas

3. **Hot Reload:**
   - Bitta portda hot reload ishlamaydi
   - Hot reload kerak bo'lsa, alohida Vite server ishlatib (`localhost:5173`)

4. **Performance:**
   - Production da Nginx static fayllarni serve qilishi kerak
   - Django development server production uchun emas

---

## 🐛 Muammolarni Hal Qilish

### "Frontend Not Built" Xatosi:

```bash
cd frontend
npm run build
```

### "Port 8000 Band":

```bash
# Portni bo'shatish
lsof -ti:8000 | xargs kill -9  # Linux/Mac
```

### API 404 Error:

URL to'g'riligini tekshiring:
- ✅ `/api/v1/auth/register/`
- ❌ `/api/auth/register/` (v1 yo'q)

### Frontend Yangilanmayapti:

```bash
# Frontend qayta build qiling
cd frontend
npm run build

# Browser cache tozalang (Ctrl+Shift+R)
```

---

## 🎉 Tayyor!

Endi sizda:

✅ **Backend va frontend BITTA PORTDA** (8000)
✅ **Bitta server** - Django hammasini serve qiladi
✅ **Start script** - Hammasi avtomatik
✅ **API va UI** - Birgalikda ishlaydi

### **Ishga Tushirish:**

```bash
./start.sh
```

**Keyin browser oching:** `http://localhost:8000` 🚀

---

## 📊 Qo'shimcha Ma'lumot

- **API Connection Test:** [QUICK_START.md](QUICK_START.md)
- **Project Overview:** [README.md](README.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
