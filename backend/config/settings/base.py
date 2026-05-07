'''
Base settings for Bittada Marketplace.
'''
import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
# We don't read .env here; dev.py and prod.py will do it if needed.

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-temporary-key-for-dev')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "modeltranslation",  # MUHIM: django.contrib.admin dan OLDIN bo'lishi shart
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    
    # Third party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "mptt",
    "django_filters",
    "axes",
    "drf_spectacular",
    
    # Local apps
    "apps.users",
    "apps.categories",
    "apps.products",
    "apps.services",
    "apps.orders",
    "apps.escrow",
    "apps.billing",
    "apps.warehouse",
    "apps.chat",
    "apps.pages",
    "apps.seo",
    "apps.support",
    "apps.blacklist",
    "apps.notifications",
    "apps.analytics",
    "apps.integrations",
    "apps.showroom",
    "apps.media",
    "apps.api",
    "apps.dashboard",
    "apps.auth_methods",
    "apps.core",
    "apps.i18n_extra",
    "apps.variants",
    "apps.marketplace",
    "apps.management",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.management.middleware.ManagementAccessMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # i18n: shablonlarda {{ LANGUAGE_CODE }} va {{ LANGUAGE_BIDI }} ni
                # avtomatik mavjud qiladi (request.LANGUAGE_CODE'dan keladi).
                # i18n_patterns ostida til prefixi (/uz/, /ru/, /en/) bo'yicha o'zgaradi.
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "uz"
LANGUAGES = [
    ('uz', 'Uzbek'),
    ('ru', 'Русский'),
    ('en', 'English'),
]
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True
# YANGI: LOCALE_PATHS — Django'ga `locale/<lang>/LC_MESSAGES/` qaerdaligini bildiradi.
# Bunsiz `compilemessages` chiqargan `.mo` fayllar topilmaydi va {% trans %} taglari
# faqat default (LANGUAGE_CODE) tilida qaytadi (i18n switching ishlamaydi).
LOCALE_PATHS = [
    BASE_DIR / "locale",  # Loyiha root'idagi `locale/` (uz/, ru/, en/ ostida)
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

# Login URLs
# i18n_patterns ostida /uz/login/, /ru/login/, /en/login/ shaklida ishlaydi
LOGIN_URL = "/login/"
# Kirish muvaffaqiyatli bo'lganda foydalanuvchi roliga qarab yo'naltirish:
# - customer → /profile/
# - seller/staff → /dashboard/
LOGIN_REDIRECT_URL = "/ru/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Content Security Policy (CSP) Settings
# VAQTINCHA O'CHIRILGAN: django-csp o'rnatilmagan
# CSP_FRAME_ANCESTORS = (
#     "'self'", 
#     "https://oauth.telegram.org", 
#     "https://accounts.google.com", 
#     "http://localhost:8000", 
#     "http://127.0.0.1:8000",
#     "http://localhost",
#     "http://127.0.0.1"
# )
# CSP_REFERRER_POLICY = "strict-origin-when-cross-origin"
# CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://telegram.org", "https://accounts.google.com")
# CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
# CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
# CSP_IMG_SRC = ("'self'", "data:", "https://telegram.org")
# Google Auth sozlamalari
GOOGLE_OAUTH_CLIENT_ID = env("GOOGLE_OAUTH_CLIENT_ID", default="")

# Telegram Auth sozlamalari
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_BOT_USERNAME = env("TELEGRAM_BOT_USERNAME", default="")
TELEGRAM_BOT_ID = env("TELEGRAM_BOT_ID", default="")