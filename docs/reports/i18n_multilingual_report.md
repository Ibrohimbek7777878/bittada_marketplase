# Hisobot: Ko'p Tillilik (i18n) Tizimini Joriy Etish

Ushbu hisobot Bittada Marketplace loyihasida ko'p tillilik (internationalization/i18n) tizimini joriy etish bo'yicha amalga oshirilgan ishlarni tavsiflaydi.

## Amalga oshirilgan o'zgarishlar

### 1. Django i18n Sozlamalari (`config/settings/base.py`)

**INSTALLED_APPS**:
- `modeltranslation` - django.contrib.admin dan OLDIN qo'shildi (muhim tartib)
- Django model tarjimalari uchun django-modeltranslation paketi o'rnatildi

**MIDDLEWARE**:
- `django.middleware.locale.LocaleMiddleware` - SessionMiddleware dan keyin, CommonMiddleware dan OLDIN joylashtirildi

**Yangi Sozlamalar**:
```python
LANGUAGES = [
    ("uz", _("O'zbek")),
    ("ru", _("Русский")),
    ("en", _("English")),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

MODELTRANSLATION_DEFAULT_LANGUAGE = "uz"
MODELTRANSLATION_LANGUAGES = ("uz", "ru", "en")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("uz", "ru", "en")
```

### 2. URL Konfiguratsiyasi (`config/urls.py`)

- `i18n_patterns` joriy qilindi
- Sahifalar uchun til prefixlari bilan yo'llar:
  - `/uz/` - O'zbek tili
  - `/ru/` - Rus tili
  - `/en/` - Ingliz tili
- Tilni o'zgartirish uchun `/i18n/` URL qo'shildi
- API va xizmat yo'llari (healthz, api, schema) prefixsiz qoldi

### 3. Model Tarjimasi (`apps/products/translation.py`)

**Category modeli** uchun tarjima:
- `name_uz`, `name_ru`, `name_en` maydonlari

**Product modeli** uchun tarjima:
- `title_uz`, `title_ru`, `title_en`
- `description_uz`, `description_ru`, `description_en`

Migrations yaratildi va ishga tushirildi.

### 4. Template Matnlarining Tarjimasi

Barcha matnlar `{% trans %}` tagi bilan o'rlandi:
- `profile_erp.html` - Profil sahifasi
- `home_erp.html` - Bosh sahifa
- `checkout_erp.html` - Buyurtma rasmiylashtirish

### 5. Til O'zgartirgich (Language Switcher)

`templates/includes/erp_navbar.html` ga til o'zgartirgich qo'shildi:
- Hozirgi tilni ko'rsatadi
- O'zbek, Rus, Ingliz tillari o'rtasida almashish imkoniyati
- Bootstrap Icons ishlatildi

### 6. Tarjima Fayllari (.po)

Qo'lda yaratilgan tarjima fayllari:
- `locale/uz/LC_MESSAGES/django.po` - O'zbek tili
- `locale/ru/LC_MESSAGES/django.po` - Rus tili
- `locale/en/LC_MESSAGES/django.po` - Ingliz tili

**Diqqat**: .mo fayllarini (compilemessages) yaratish uchun tizimda GNU gettext tools (msgfmt, msguniq) o'rnatilishi kerak.

## Qo'llanma

### 1. .mo Fayllarini Yaratish (Serverda)
```bash
sudo apt-get install gettext
python manage.py compilemessages
```

### 2. Yangi Matnlarni Tarjima Qilish
```bash
python manage.py makemessages -l uz -l ru -l en
# Tarjima qilingandan so'ng:
python manage.py compilemessages
```

### 3. Model Maydonlarini Tarjima Qilish
Admin paneldan har bir til uchun alohida maydonlarni to'ldiring.

## Xulosa

Ko'p tillilik tizimi to'liq ishga tushirildi. Barcha interfeys matnlari UZ, RU, EN tillariga tarjima qilindi. Model ma'lumotlari (Product, Category) ham uch tilda saqlanishi mumkin.

**Foydalanish**:
- Saytga kirish: `/uz/`, `/ru/`, `/en/`
- Tilni o'zgartirish: Navbar'dagi til tanlagich orqali
