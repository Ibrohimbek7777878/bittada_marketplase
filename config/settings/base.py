"""
Base settings for Bittada Marketplace.
"""
import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
# We don't read .env here; dev.py and prod.py will do it if needed.

# Vaqtincha xavfsizlik va xatolikni oldini olish uchun Hardcoded SECRET_KEY
SECRET_KEY = 'django-insecure-temporary-key-for-dev'

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
    # "django_extensions", # O'chirilgan (ModuleNotFoundError bermasligi uchun)
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
    # ─────────────────────────────────────────────────────────────────────
    # Bittada ERP — alohida boshqaruv ekotizimi (2026-05-02 qo'shildi)
    # /dashboard/* HTML sahifalar va /dashboard/api/v1/* DRF API
    # Mustaqil yangi ilova — Django'ning standart admin'iga bog'liq emas.
    # ─────────────────────────────────────────────────────────────────────
    "apps.management",  # AppConfig: apps.management.apps.ManagementConfig
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # MUHIM: CommonMiddleware dan OLDIN bo'lishi shart
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # request.user'ni o'rnatadi
    # ─────────────────────────────────────────────────────────────────────
    # Bittada ERP — Firewall middleware (2026-05-02)
    # AuthenticationMiddleware'dan KEYIN bo'lishi shart (request.user'ga ehtiyoji bor).
    # /dashboard/* yo'llariga ruxsatsiz so'rovlarni /login/ ga yo'naltiradi.
    # ─────────────────────────────────────────────────────────────────────
    "apps.management.middleware.ManagementAccessMiddleware",  # ERP Firewall
    # ─────────────────────────────────────────────────────────────────────
    # Customer Admin Blocker — Mijozlardan admin panelga kirishni cheklash
    # AuthenticationMiddleware va ManagementAccessMiddleware'dan KEYIN.
    # ─────────────────────────────────────────────────────────────────────
    "apps.users.middleware.BlockCustomerAdminAccessMiddleware",  # Customer admin block
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

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

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────────────────────────────────────
# KO'P TILLILIK (I18N) SOZLAMALARI (TZ §4)
# ─────────────────────────────────────────────────────────────────────────────
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ("uz", _("O'zbek")),
    ("ru", _("Русский")),
    ("en", _("English")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

MODELTRANSLATION_DEFAULT_LANGUAGE = "uz"
MODELTRANSLATION_LANGUAGES = ("uz", "ru", "en")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("uz", "ru", "en")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # Birlamchi PK turi (BigInt) — barcha modellar uchun standart
AUTH_USER_MODEL = "users.User"  # Foydalanuvchi modeli (apps.users.models.User) — Django auth tizimi shu modelni ishlatadi

# ─────────────────────────────────────────────────────────────────────────────
# AUTH REDIRECT SOZLAMALARI
# Maqsad: Django'ning standart "Please log in" sahifasi (/accounts/login/) ishlamasin —
# barcha "login_required" yo'naltirishlari bizning chiroyli ERP login sahifasiga (/login/) tushsin.
# Shuningdek, super-admin/ ga kirishga harakat qilgan oddiy foydalanuvchi
# Django admin'ning standart login formasini ko'rmaydi — u ham /login/ ga yo'naltiriladi
# (custom view'larda staff_member_required(login_url=settings.LOGIN_URL) ishlatiladi).
# ─────────────────────────────────────────────────────────────────────────────
LOGIN_URL = "/login/"  # Tizimga kirish sahifasi yo'li (apps.products.views.login_view)
LOGIN_REDIRECT_URL = "/"  # Muvaffaqiyatli kirishdan keyin yo'naltiriladigan default sahifa (Bosh sahifa)
LOGOUT_REDIRECT_URL = "/"  # Tizimdan chiqqandan keyin Bosh sahifaga qaytarish

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
