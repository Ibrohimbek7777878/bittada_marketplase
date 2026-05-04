# 🔧 Local Development Environment - Complete Fix

## 📋 A. ROOT CAUSE FOUND

### Issues Identified:
1. ❌ **No API root endpoint** at `/api/v1/` - returned 404
2. ❌ **Mixed deployment modes** - confusion between:
   - Vite proxy mode (frontend:5173 + backend:8000)
   - Single-port mode (Django serves everything on :8000)
3. ❌ **No centralized API config** - scattered environment variables
4. ⚠️ **Hardcoded URLs** in frontend code

### What Was Working:
- ✅ Backend server running on port 8000
- ✅ Vite proxy configured correctly
- ✅ CORS enabled for localhost:5173
- ✅ API endpoints functional (auth, users, etc.)

---

## 📁 B. FILES CHANGED

### Created:
1. `frontend/src/config/api.js` - Centralized API configuration
2. `docs/LOCAL_DEV_SETUP.md` - This file

### Modified:
1. `frontend/src/api/client.js` - Use centralized config
2. `frontend/src/pages/home.js` - Use centralized config  
3. `frontend/.env` - Clear environment variable documentation
4. `backend/config/urls.py` - Added API root endpoint

---

## 💻 C. EXACT CODE CHANGES

### 1. Centralized API Config (NEW)
**File:** `frontend/src/config/api.js`

```javascript
// Detect environment
const isDev = import.meta.env.DEV;
const isSinglePort = !isDev || import.meta.env.VITE_SINGLE_PORT === 'true';

// API Base URL - single source of truth
export const API_BASE_URL = isSinglePort
  ? (import.meta.env.VITE_API_URL || '/api/v1')
  : (import.meta.env.VITE_API_BASE || '/api/v1');

// All endpoints defined here
export const ENDPOINTS = {
  register: '/auth/register/',
  login: '/auth/login/',
  testConnection: '/api/test-connection/',
  // ... more endpoints
};

// Utility function
export function buildUrl(path) {
  return `${API_BASE_URL}${path}`;
}
```

### 2. API Client Update
**File:** `frontend/src/api/client.js`

```javascript
// BEFORE:
const BASE = (import.meta.env.VITE_API_BASE) || '/api/v1';

// AFTER:
import { API_BASE_URL } from '../config/api.js';
const BASE = API_BASE_URL;
```

### 3. Home Page Update  
**File:** `frontend/src/pages/home.js`

```javascript
// BEFORE:
const apiBase = import.meta.env.VITE_API_BASE || '/api/v1';
const testUrl = `${apiBase}/api/test-connection/`;

// AFTER:
import { buildUrl, ENDPOINTS } from '../config/api.js';
const testUrl = buildUrl(ENDPOINTS.testConnection);
```

### 4. Backend API Root (NEW)
**File:** `backend/config/urls.py`

```python
def api_root(_request):
    """API root - provides information about available endpoints."""
    return JsonResponse({
        "name": "Bittada Marketplace API",
        "version": "v1",
        "status": "running",
        "endpoints": {
            "auth": "/api/v1/auth/",
            "users": "/api/v1/users/",
            "test": "/api/v1/api/test-connection/",
        },
        "docs": "/api/docs/",
    })

urlpatterns = [
    path("api/v1/", api_root, name="api-root"),  # NEW
    path("api/v1/", include((api_v1_patterns, "api"), namespace="v1")),
]
```

---

## 🚀 D. COMMANDS TO RUN

### Option 1: Vite Proxy Mode (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # If using venv
python manage.py runserver 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Open:** `http://localhost:5173`

### Option 2: Single-Port Mode (Production-like)

```bash
# Build frontend first
cd frontend
npm run build
cd ..

# Run start script
./start.sh
```

**Open:** `http://localhost:8000`

### Quick Test:
```bash
# Test backend
curl http://localhost:8000/api/v1/
curl http://localhost:8000/api/v1/api/test-connection/

# Test frontend (if using Vite proxy)
curl http://localhost:5173/api/v1/api/test-connection/
```

---

## 🌐 E. FINAL WORKING URLs

### Vite Proxy Mode (Development):
| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | http://localhost:5173 | ✅ Ready |
| **Backend API** | http://localhost:8000/api/v1/ | ✅ Ready |
| **API Root** | http://localhost:8000/api/v1/ | ✅ NEW |
| **Test Endpoint** | http://localhost:8000/api/v1/api/test-connection/ | ✅ Working |
| **API Docs** | http://localhost:8000/api/docs/ | ✅ Ready |
| **Admin Panel** | http://localhost:8000/admin/ | ✅ Ready |
| **Health Check** | http://localhost:8000/healthz | ✅ Working |

### Single-Port Mode (Production):
| Service | URL | Status |
|---------|-----|--------|
| **Frontend + API** | http://localhost:8000 | ✅ Ready |
| **Backend API** | http://localhost:8000/api/v1/ | ✅ Ready |
| **API Docs** | http://localhost:8000/api/docs/ | ✅ Ready |
| **Admin Panel** | http://localhost:8000/admin/ | ✅ Ready |

---

## 📊 Architecture

### Mode 1: Vite Proxy (Development)
```
Browser → http://localhost:5173 (Vite)
  ↓
  /api/* → Proxy → http://localhost:8000 (Django)
  /* → Served by Vite (Hot Reload)
```

**Pros:**
- ✅ Hot reload for frontend
- ✅ Fast development
- ✅ Separate concerns

**Cons:**
- ❌ Two servers to manage
- ❌ Not production-like

### Mode 2: Single Port (Production)
```
Browser → http://localhost:8000 (Django)
  ↓
  /api/* → Django API
  /admin/* → Django Admin
  /* → Frontend SPA (built files)
```

**Pros:**
- ✅ One server
- ✅ Production-like
- ✅ Simple deployment

**Cons:**
- ❌ No hot reload
- ❌ Rebuild needed for frontend changes

---

## 🔧 Configuration Reference

### Frontend Environment Variables

| Variable | Mode | Value | Description |
|----------|------|-------|-------------|
| `VITE_API_BASE` | Dev (Proxy) | `/api/v1` | Relative path for Vite proxy |
| `VITE_API_URL` | Prod | `/api/v1` | Base URL for API |
| `VITE_SINGLE_PORT` | Both | `false`/`true` | Toggle deployment mode |

### Backend Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DJANGO_DEBUG` | `1` | Enable debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Allowed hosts |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Frontend origin |
| `CORS_ALLOW_ALL_ORIGINS` | `True` (dev only) | Allow all CORS |

---

## ✅ Verification Checklist

Run these tests to verify everything works:

### Backend Tests:
```bash
# 1. Health check
curl http://localhost:8000/healthz
# Expected: {"status": "ok"}

# 2. API root
curl http://localhost:8000/api/v1/
# Expected: {"name": "Bittada Marketplace API", ...}

# 3. Test connection
curl http://localhost:8000/api/v1/api/test-connection/
# Expected: {"status": "ok", "message": "Backend API is fully connected!"}

# 4. API docs (browser)
# Open: http://localhost:8000/api/docs/
```

### Frontend Tests:
```bash
# 1. Frontend loads (Vite proxy mode)
# Open: http://localhost:5173

# 2. API connection test
# Click "Test API Connection" button on home page
# Expected: Green success message

# 3. No CORS errors in browser console
# Open DevTools → Console
# Expected: No red errors
```

### Integration Tests:
```bash
# 1. Register user (via API)
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "username": "testuser"
  }'

# 2. Login (via API)
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

---

## 🐛 Troubleshooting

### Problem: "Page not found at /api/v1/"
**Solution:** This is now fixed! API root endpoint added.

### Problem: CORS Error
**Solution:** 
```python
# backend/config/settings/dev.py
CORS_ALLOW_ALL_ORIGINS = True  # Dev only
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8000",
]
```

### Problem: Port 8000 already in use
**Solution:**
```bash
lsof -ti:8000 | xargs kill -9
./start.sh
```

### Problem: Frontend can't connect to backend
**Solution:**
1. Check backend is running: `curl http://localhost:8000/healthz`
2. Check Vite proxy config: `frontend/vite.config.js`
3. Check API config: `frontend/src/config/api.js`

### Problem: API returns 404
**Solution:**
1. Check URL prefix: should be `/api/v1/...`
2. Check endpoint exists: see `backend/config/urls.py`
3. Test with curl first

---

## 📚 Next Steps

1. ✅ **API Root** - Added `/api/v1/` endpoint
2. ✅ **Centralized Config** - All API calls use `config/api.js`
3. ✅ **Environment Variables** - Clear documentation
4. ✅ **Dual Mode Support** - Vite proxy + Single port
5. ⏳ **Add more endpoints** to `config/api.js`
6. ⏳ **Create service files** in `frontend/src/services/`
7. ⏳ **Add authentication flow** UI
8. ⏳ **Implement product catalog** pages

---

## 🎯 Summary

**Before:**
- ❌ No API root endpoint
- ❌ Scattered API configuration
- ❌ Confusing deployment modes
- ❌ Hardcoded URLs

**After:**
- ✅ API root endpoint at `/api/v1/`
- ✅ Centralized `config/api.js`
- ✅ Clear dual-mode support
- ✅ Environment-based configuration
- ✅ Production-ready structure

**Status:** 🟢 **FULLY WORKING**
