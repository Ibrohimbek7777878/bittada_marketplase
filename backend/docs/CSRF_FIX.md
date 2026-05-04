# 🔐 CSRF Protection - Complete Fix & Explanation

## THE REAL ISSUE

You're seeing "CSRF Failed: CSRF token missing" because:

1. **Django's CSRF middleware is enabled** (correct!)
2. **Frontend sends POST requests** without CSRF token
3. **JWT Bearer tokens don't automatically handle CSRF**

---

## UNDERSTANDING CSRF vs JWT

### **Session-Based Auth (Needs CSRF Protection):**
```
Browser → POST /login → Server sets session cookie
Browser → POST /register → Sends session cookie automatically
⚠️ Problem: Malicious site can also send requests with your cookie!
✅ Solution: Require CSRF token in custom header
```

### **JWT Bearer Auth (CSRF NOT Required):**
```
Browser → POST /login → Server returns JWT token
Browser stores JWT in localStorage
Browser → POST /register → Sends JWT in Authorization header
✅ No cookie sent automatically = No CSRF risk!
✅ No CSRF protection needed!
```

---

## SOLUTION APPLIED

### **Option Chosen: JWT + CSRF Double Protection**

We implemented BOTH for maximum security:

1. ✅ JWT Bearer tokens in `Authorization` header
2. ✅ CSRF token in `X-CSRFToken` header
3. ✅ Cookies with `credentials: 'include'`

---

## FILES MODIFIED

### **Backend (3 files):**

#### 1. `backend/config/settings/base.py`
```python
# BEFORE:
CSRF_COOKIE_HTTPONLY = True  # JavaScript can't read

# AFTER:
CSRF_COOKIE_HTTPONLY = False  # JavaScript CAN read
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
```

#### 2. `backend/apps/api/csrf_views.py` (NEW)
```python
@require_GET
def get_csrf_token(request):
    """Dedicated endpoint to obtain CSRF cookie for SPA."""
    csrf_token = get_token(request)
    return JsonResponse({
        'csrfToken': csrf_token,
        'message': 'CSRF token cookie has been set'
    })
```

#### 3. `backend/apps/api/urls.py`
```python
urlpatterns = [
    path("test-connection/", api_test_connection),
    path("csrf-token/", get_csrf_token),  # NEW
]
```

### **Frontend (2 files):**

#### 1. `frontend/src/api/client.js`
```javascript
// Get CSRF token from cookie
export function getCSRFToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  
  return cookieValue;
}

// Fetch CSRF token on app load
export async function ensureCSRFToken() {
  const existingToken = getCSRFToken();
  if (existingToken) {
    return existingToken;
  }
  
  try {
    const csrfUrl = buildUrl('/api/csrf-token/');
    await fetch(csrfUrl, {
      method: 'GET',
      credentials: 'include',
    });
    return getCSRFToken();
  } catch (error) {
    console.warn('Failed to fetch CSRF token:', error);
    return null;
  }
}

// Include CSRF token in API calls
export async function apiCall(method, path, data = null) {
  const csrfToken = getCSRFToken();
  
  const options = {
    method: method.toUpperCase(),
    headers: {
      'Content-Type': 'application/json',
      // Include CSRF token for unsafe methods
      ...(csrfToken && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) && {
        'X-CSRFToken': csrfToken,
      }),
    },
    credentials: 'include', // Include cookies
  };
  
  // ... rest of function
}
```

#### 2. `frontend/src/main.js`
```javascript
import { ensureCSRFToken } from './api/client.js';

// Ensure CSRF token before initializing app
ensureCSRFToken().then(() => {
  console.log('✅ CSRF token loaded');
  initRouter();
}).catch((error) => {
  console.warn('⚠️ CSRF token not loaded:', error);
  initRouter();
});
```

---

## CORS CONFIGURATION

### **Backend Settings (Already Correct):**

```python
# backend/config/settings/dev.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8000",
]
CORS_ALLOW_ALL_ORIGINS = True  # Dev only
CORS_ALLOW_CREDENTIALS = True  # ✅ Important!

CORS_ALLOW_HEADERS = [
    'accept',
    'content-type',
    'authorization',
    'x-csrftoken',  # ✅ CSRF header allowed
    'x-requested-with',
]
```

---

## HOW IT WORKS NOW

### **Request Flow:**

```
1. User opens app (http://localhost:8000)
   ↓
2. Frontend calls: GET /api/v1/api/csrf-token/
   ↓
3. Django responds with:
   - JSON: {"csrfToken": "abc123..."}
   - Set-Cookie: csrftoken=abc123...; Path=/;
   ↓
4. Frontend reads cookie: getCSRFToken()
   ↓
5. User fills registration form
   ↓
6. Frontend sends POST /api/v1/auth/register/
   Headers:
   - Content-Type: application/json
   - Authorization: Bearer <JWT> (if logged in)
   - X-CSRFToken: abc123... ← From cookie
   - Cookie: csrftoken=abc123... ← Automatic
   ↓
7. Django validates:
   - CSRF token in header matches cookie ✅
   - JWT token valid (if present) ✅
   ↓
8. Request succeeds! ✅
```

---

## TESTING

### **1. Test CSRF Token Endpoint:**
```bash
curl -v http://localhost:8000/api/v1/api/csrf-token/

# Expected Response Headers:
# Set-Cookie: csrftoken=abc123...; Path=/

# Expected Body:
{"csrfToken": "abc123...", "message": "CSRF token cookie has been set"}
```

### **2. Test Registration with CSRF:**
```bash
# Step 1: Get CSRF token
curl -c cookies.txt http://localhost:8000/api/v1/api/csrf-token/

# Step 2: Extract token
CSRF=$(grep csrftoken cookies.txt | awk '{print $NF}')

# Step 3: Register with CSRF token
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -b cookies.txt \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!"
  }'

# Expected: 201 Created with user data
```

### **3. Test in Browser:**
```
1. Open: http://localhost:8000/register
2. Open DevTools → Network tab
3. Fill form and submit
4. Check request headers:
   - X-CSRFToken: abc123... ✅
   - Cookie: csrftoken=abc123... ✅
5. Check response: 201 Created ✅
```

---

## PRODUCTION DEPLOYMENT

### **Settings for Production:**

```python
# backend/config/settings/prod.py

# HTTPS required
CSRF_COOKIE_SECURE = True  # Only send over HTTPS
SESSION_COOKIE_SECURE = True

# CSRF still works
CSRF_COOKIE_HTTPONLY = False  # SPA needs to read it
CSRF_COOKIE_SAMESITE = 'Lax'  # Protection against CSRF

# CORS - restrict to your domain
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]
CORS_ALLOW_CREDENTIALS = True
```

### **Nginx Configuration:**
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    # Backend
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # CSRF headers
        proxy_pass_request_headers on;
    }
    
    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
        root /var/www/frontend/dist;
    }
}
```

---

## ALTERNATIVE: DISABLE CSRF FOR JWT ONLY

If you want to use **JWT only** (no CSRF), you can exempt API views:

### **Option 1: Exempt Specific Views**
```python
from django.views.decorators.csrf import csrf_exempt

class RegisterView(APIView):
    @csrf_exempt  # Only for this view
    def post(self, request):
        # ...
```

### **Option 2: Use JWT Authentication Class**
```python
# backend/config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}
```

**Note:** JWT in Authorization header is NOT vulnerable to CSRF, so you can safely disable CSRF for authenticated endpoints.

---

## BEST PRACTICE RECOMMENDATION

### **For Your Project (JWT + SPA):**

✅ **KEEP CSRF Protection** because:
1. You have session-based features (admin panel)
2. Defense in depth (multiple security layers)
3. Compliance requirements
4. No performance impact

✅ **Use JWT for API authentication**
- Bearer tokens in Authorization header
- Stored in localStorage
- Automatic refresh on expiry

✅ **Use CSRF for session-based endpoints**
- Admin panel
- Django forms
- Any endpoint using cookies

---

## SUMMARY

### **What Was Fixed:**
1. ✅ Created `/api/v1/api/csrf-token/` endpoint
2. ✅ Enabled JavaScript to read CSRF cookie
3. ✅ Frontend fetches CSRF token on load
4. ✅ Frontend sends `X-CSRFToken` header on POST/PUT/PATCH/DELETE
5. ✅ CORS configured with credentials support
6. ✅ Production-ready settings

### **Current Status:**
🟢 **CSRF Protection Working**

### **Test Results:**
- ✅ CSRF token endpoint works
- ✅ Frontend reads CSRF cookie
- ✅ API calls include CSRF token
- ✅ Registration succeeds without errors
- ✅ No "CSRF Failed" errors

### **How to Verify:**
```bash
# Restart server
./start.sh

# Open browser
http://localhost:8000/register

# Open DevTools → Console
# Should see: "✅ CSRF token loaded"

# Submit form → Check Network tab
# Request headers should include: X-CSRFToken: abc123...

# Response: 201 Created ✅
```

---

**CSRF protection is now fully working with JWT authentication in a production-ready configuration!** 🔐
