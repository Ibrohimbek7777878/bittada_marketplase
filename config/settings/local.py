"""
Local development settings — Django templates mode.
No Docker, no Vite, pure Django.
"""
from __future__ import annotations

from .base import *  # noqa: F401,F403

# DEBUG mode
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

# Database — SQLite for local dev (no PostgreSQL needed)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Cache — dummy for local dev (Redis not needed)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Session backend — use database (not Redis cached_db)
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_CACHE_ALIAS = None

# Static files — local storage
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Email — console backend for testing
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable Celery for local dev (no Redis needed)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = None
CELERY_RESULT_BACKEND = None

# Disable Channels/Redis for local dev
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Debug toolbar (optional)
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# CSRF trusted origins for local
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
