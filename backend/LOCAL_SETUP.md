# Bittada — Lokal Ishga Tushirish (Django Templates)

Django lokal kompyuteringizda ishlaydi, frontend esa Django templates.

## Talablar

- Python 3.12+
- pip
- virtualenv (tavsiya etiladi)

## O'rnatish

### 1. Repository'ni klonlash

```bash
cd /home/ibrohim/Desktop/client_baza/bittada_market_ekosistema\ \(2\)
```

### 2. Virtual muhit yaratish

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# yoki
.venv\Scripts\activate  # Windows
```

### 3. Paketlarni o'rnatish

```bash
cd backend
pip install -r requirements.txt
```

### 4. Ma'lumotlar bazasini sozlash

```bash
python manage.py migrate --run-syncdb
```

### 5. Static fayllarni yig'ish

```bash
python manage.py collectstatic --noinput
```

### 6. Superuser yaratish (ixtiyoriy)

```bash
python manage.py createsuperuser
```

## Ishga tushirish

### Variant 1: Skript orqali (tavsiya etiladi)

```bash
cd /home/ibrohim/Desktop/client_baza/bittada_market_ekosistema\ \(2\)
./run_local.sh
```

### Variant 2: Qo'lda

```bash
cd backend
export DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py runserver 0.0.0.0:8000
```

## URL'lar

| URL | Tavsif |
|-----|--------|
| http://127.0.0.1:8000 | Bosh sahifa |
| http://127.0.0.1:8000/admin | Django Admin |
| http://127.0.0.1:8000/shop/ | Do'kon sahifasi |
| http://127.0.0.1:8000/category/{slug}/ | Kategoriya |
| http://127.0.0.1:8000/product/{uuid}/ | Mahsulot detali |

## Sozlamalar

Lokal sozlamalar: `backend/config/settings/local.py`

- **Database**: SQLite (`db.sqlite3`)
- **Cache**: Dummy (Redis shart emas)
- **Celery**: Eager mode (background tasklar sinxron ishlaydi)
- **Email**: Console (email terminalga chiqadi)

## Muammolarni hal qilish

### `ModuleNotFoundError: No module named 'config'`

```bash
cd backend
export PYTHONPATH=/home/ibrohim/Desktop/client_baza/bittada_market_ekosistema\ \(2\)/backend:$PYTHONPATH
```

### Static fayllar yuklanmayapti

```bash
python manage.py collectstatic --clear --noinput
```

### Ma'lumotlar bazasi xatosi

```bash
rm db.sqlite3
python manage.py migrate --run-syncdb
```

## Loyiha Tuzilishi

```
bittada_market_ekosistema/
├── backend/
│   ├── apps/
│   │   └── products/
│   │       ├── views.py       # Template views
│   │       ├── urls.py        # URL routes
│   │       └── models.py      # Models
│   ├── templates/
│   │   ├── base.html          # Asosiy shablon
│   │   ├── home.html          # Bosh sahifa
│   │   ├── shop.html          # Do'kon
│   │   ├── product_detail.html
│   │   └── includes/
│   │       └── product_card.html
│   ├── config/
│   │   └── settings/
│   │       ├── local.py       # Lokal sozlamalar
│   │       └── base.py        # Umumiy sozlamalar
│   └── requirements.txt
├── run_local.sh               # Ishga tushirish skripti
└── LOCAL_SETUP.md             # Bu fayl
```

## Xususiyatlar

- ✅ **Django Templates** — Server-side rendering
- ✅ **SQLite** — Oson sozlash
- ✅ **No Docker** — Toza lokal ish
- ✅ **No Redis** — Cache shart emas
- ✅ **No Celery** — Tasklar sinxron
- ✅ **Auto superuser** — Birinchi ishga tushirishda
