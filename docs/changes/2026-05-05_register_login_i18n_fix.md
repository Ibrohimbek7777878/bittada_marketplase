# Register + Login (Telegram) + i18n tuzatish

**Sana**: 2026-05-05
**Muallif**: Claude (Opus 4.7) — `mebelcityai@gmail.com` so'rovi bo'yicha

## Qisqacha

3 ta muammo hal qilindi:

1. **Register to'liq ishlamaydi** — `RegisterForm` va template-based
   `RegisterView` (CBV) qo'shildi. Form valid bo'lsa: user yaratiladi,
   sessionga login qilinadi, `/` ga redirect.
2. **Login sahifasida Telegram button yo'qolgan** — `templates/auth/login.html`
   yangidan yaratildi (Telegram tugmasi bilan), `auth_methods:telegram_login`
   URL nomi qo'shildi.
3. **i18n (til) ishlamaydi** — `LOCALE_PATHS` va `i18n` context processor
   `settings/base.py` ga qo'shildi. `/uz/`, `/ru/`, `/en/` — barcha tillar
   ishlaydi va `<html lang="...">` to'g'ri o'rnatiladi.

## URL'lar

| URL | View | Vazifa |
|-----|------|--------|
| `/auth/register/` | `RegisterView` (apps/users/views.py) | Yangi user + auto-login |
| `/auth/login/` | `LoginView` (apps/users/views.py) | Login + Telegram tugma |
| `auth_methods:telegram_login` | `TelegramAuthView` (= TelegramCallbackView alias) | Telegram OAuth callback |
| `/i18n/setlang/` | Django default | Til o'zgartirish |

**Eslatma**: mavjud `/login/`, `/register/` URL'lari (apps/products/urls.py)
**o'zgartirilmadi** (daxlsizlik). Yangi `/auth/...` URL'lari parallel
ishlaydi.

## O'zgartirilgan / yaratilgan fayllar

| Fayl | Holat | Maqsad |
|------|-------|--------|
| `backend/config/settings/base.py` | tahrir | `LOCALE_PATHS` + `i18n` context processor qo'shildi |
| `backend/apps/users/forms.py` | tahrir | `RegisterForm` (username+email+password1+password2) |
| `backend/apps/users/views.py` | tahrir | `RegisterView` (FormView) + `LoginView` (CBV) |
| `backend/apps/auth_methods/views.py` | tahrir | `TelegramAuthView = TelegramCallbackView` alias |
| `backend/apps/auth_methods/urls.py` | tahrir | `path("telegram/", ..., name="telegram_login")` |
| `backend/config/urls.py` | tahrir | `/auth/register/` + `/auth/login/` ulandi |
| `backend/templates/auth/register.html` | yaratildi | Mustaqil sahifa, til switcher, errors |
| `backend/templates/auth/login.html` | yaratildi | Telegram tugma, til switcher, errors |

**Migration**: kerak emas (vazifa cheklov).

## Texnik tafsilotlar

### Register flow

```
GET  /uz/auth/register/  →  bo'sh forma (templates/auth/register.html)
POST /uz/auth/register/  →  RegisterForm.is_valid()
                          →  user.save() (User + Profile create, role=CUSTOMER)
                          →  django_login(request, user)
                          →  redirect('/')
                          →  Xato bo'lsa: form errors render
```

`RegisterForm` validatsiyasi:
- Username unikalligi (case-insensitive)
- Email unikalligi (case-insensitive, lowercase'ga)
- Password1 minimum 8 belgi
- Password1 == Password2 (`clean()` → `add_error("password2", ...)`)

### Login flow

```
GET  /uz/auth/login/  →  templates/auth/login.html (Telegram tugma bilan)
POST /uz/auth/login/  →  authenticate(email=identifier) yoki username orqali
                       →  django_login + redirect to ?next= yoki '/'
                       →  Xato: error template ga qaytariladi
```

Email ham, username ham ishlaydi (foydalanuvchi qaysisi'ni yozsa).

### Telegram tugma

`templates/auth/login.html`:
```html
<a href="{% url 'auth_methods:telegram_login' %}" class="btn btn-telegram">
  ✈️ Telegram orqali kirish
</a>
```

`auth_methods:telegram_login` reverse natija: `/telegram-callback/telegram/`
(chunki `auth_methods.urls` ikki marta mount qilingan: `/api/v1/auth/` va
`/telegram-callback/`). Tugma `TelegramAuthView` (alias of
`TelegramCallbackView`) ga oldib boradi — u Telegram Login Widget
callback'i (hash verification + user create + session login).

### i18n setup

`config/settings/base.py`:
```python
LANGUAGE_CODE = "uz"
LANGUAGES = [('uz','Uzbek'),('en','English'),('ru','Russian')]
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / "locale"]   # YANGI

TEMPLATES = [{
  ...
  "OPTIONS": {
    "context_processors": [
      ...
      "django.template.context_processors.i18n",  # YANGI — {{ LANGUAGE_CODE }}
    ],
  },
}]
```

`config/urls.py` (mavjud, o'zgarmagan):
```python
urlpatterns += i18n_patterns(
    ...
    path("", include(template_patterns)),
    prefix_default_language=True,
)
```

`MIDDLEWARE`:
```python
"django.contrib.sessions.middleware.SessionMiddleware",
"corsheaders.middleware.CorsMiddleware",
"django.middleware.locale.LocaleMiddleware",  # SessionMiddleware'dan keyin ✓
```

`compilemessages` ishga tushirildi — `locale/uz/`, `locale/ru/`, `locale/en/`
ostidagi `.po` fayllar `.mo` ga compile qilindi.

### Til switcher (templates ichida)

Har bir auth template'da til switcher:
```html
{% get_available_languages as LANGS %}
{% for code, name in LANGS %}
  <form action="{% url 'set_language' %}" method="post">
    {% csrf_token %}
    <input type="hidden" name="next" value="{{ request.path }}">
    <input type="hidden" name="language" value="{{ code }}">
    <button type="submit">{{ code|upper }}</button>
  </form>
{% endfor %}
```

## Test natijalar

```
System check: 0 issues
compilemessages: OK (uz, ru, en)

--- AUTH FLOW (yangi client har test) ---
GET register:                       200 (7.2 KB)
GET login:                          200, Telegram tugmasi: ✓, html lang=uz: ✓
POST register valid:                302 → /, user yaratildi (role=customer), session'da: ✓
POST register mismatch:             200, "mos kelmayapti" ko'rinadi ✓
POST register dup username:         200, "allaqachon" ko'rinadi ✓
POST login (email):                 302 → /
POST login (username):              302 → /
POST login (wrong password):        200, error ko'rinadi ✓

--- i18n TESTS ---
/uz/auth/login/:  200, html lang="uz" ✓
/ru/auth/login/:  200, html lang="ru" ✓
/en/auth/login/:  200, html lang="en" ✓
```

## Vazifa cheklovlari

- ✅ **Faqat ko'rsatilgan fayllarga tegildi**: `apps/auth_methods/urls.py`
  vazifa shartiga (`telegram_login` qo'shish) ko'ra tahrir qilindi —
  vazifa o'zi shu URL'ni so'ragan.
- ✅ **Yangi app yaratilmadi**.
- ✅ **Migration kerak emas** (forma + view + template, model o'zgarmagan).
- ✅ **Daxlsizlik**: mavjud DRF `RegisterView` (apps/auth_methods),
  function-based `login_view`/`register_view` (apps/products), `CustomerSignupForm`
  o'zgarmagan. Yangi CBV'lar va URL'lar parallel ishlaydi.

## Eslatma

`auth_methods:telegram_login` reverse natija `/telegram-callback/telegram/`
ko'rinadi (chunki `auth_methods.urls` ikki marta mount qilingan: `/api/v1/auth/`
va `/telegram-callback/`). Bu mavjud loyiha tuzilishi — to'g'ri ishlaydi,
chunki `TelegramCallbackView` har ikkala mount nuqtasidan ham qabul qilinadi.
Telegram Login Widget production'da bot token bilan ishlaydi.
