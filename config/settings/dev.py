"""Development settings — loose CORS, local SMTP, debug toolbar, .env file load."""
from __future__ import annotations

import os
from pathlib import Path
import os

# import environ  # disabled for dev

class MockEnv:
    def __call__(self, key, default=None):
        return default
    def bool(self, key, default=False):
        return default
    def list(self, key, default=None):
        return default if default is not None else []
    def int(self, key, default=0):
        return int(default)
env = MockEnv()

# _REPO_ROOT = Path(__file__).resolve().parents[3]
# env.read_env(os.fspath(_REPO_ROOT / ".env"))

from .base import *  # noqa: E402, F401, F403
from .base import INSTALLED_APPS, MIDDLEWARE, env  # noqa: E402

DEBUG = True
ALLOWED_HOSTS = ["*"]

# In dev, serve frontend from Django by default (single-port mode)
# Set DJANGO_SERVE_FRONTEND=0 to disable and use separate Vite server
# DISABLED: Now using Django templates instead of SPA
SERVE_FRONTEND_IN_DEV = env.bool("DJANGO_SERVE_FRONTEND", default=False)

# CORS in dev — open to local Vite + Django.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_ALL_ORIGINS = True  # Dev only - restrict in production
CORS_ALLOW_CREDENTIALS = True

# Allow all headers for CORS
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Email goes to console.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Debug toolbar — only when running on host (not inside container).
if env.bool("DJANGO_DEBUG_TOOLBAR", default=False):
    INSTALLED_APPS += ["debug_toolbar", "django_extensions"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware", *MIDDLEWARE]
    INTERNAL_IPS = ["127.0.0.1"]

# Don't slow tests with Argon2 — switch to MD5 inside pytest.
if "PYTEST_CURRENT_TEST" in os.environ:
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# --- LOCAL CACHE & REDIS BYPASS (Backend Fix) ---
# Redis o'chiq bo'lgani uchun keshni xotiraga (LocMem) o'tkazamiz
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# WebSockets uchun Redis o'rniga xotirani ishlatamiz
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# --- REST FRAMEWORK FIX ---
# Throttling (chegaralash) darslarini o'chirib qo'yamiz (500 xatosini to'xtatish uchun)
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_CLASSES": [],
}

# --- SESSION FIX (Redis talab qilmaydi) ---
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# --- AXES (Brute-force) ni dev rejimda o'chirish ---
# Axes ba'zan 500 xatosi beradi (lock/unlock bilan), dev da o'chiriladi
AXES_ENABLED = False

# --- AUTH BACKEND (Axes + ModelBackend) ---
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",  # Axes brute-force protection (TZ §20 Security)
    "django.contrib.auth.backends.ModelBackend",
]

# --- PASSWORD HASHER (Argon2 talab qilmaydi) ---
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",   # birinchi — dev uchun
    "django.contrib.auth.hashers.Argon2PasswordHasher",   # agar o'rnatilgan bo'lsa
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
