# 🔴 QOIDALAR (RULES) — MAJBURIY!

> [!IMPORTANT]
> 1. **Daxlsizlik (Safety)**: Yangi funksiyalar qo'shilganda mavjud fayllar va funksiyalarning ishlashiga zarar yetkazmaslik, ularning o'zagini o'zgartirmaslik shart. Yangi kod loyihaning boshqa qismlariga shikast yetkazmasligi yoki ularning mantiqini buzib yubormasligi lozim.
> 2. **Tushunarlilik (Comments)**: Har bir kod qatori (har bir qator!) AI va dasturchi tushunadigan qilib batafsil kommentariyalar bilan yozilishi kerak.
> 3. **Hujjatlashtirish (Docs)**: O'zgartirilgan har bir yangi fayl haqida alohida `.md` fayl yaratiladi. Unda qanday o'zgarish kiritildi, nega kiritildi va qanday muammoga yechim bo'lgani yoziladi.
> 4. **README Integrity**: Ushbu qoidalar har doim README.md faylining eng yuqorisida turishi shart.
> 5. **Admin Login**: Admin panelga kirish: `adminbittada@gmail.com` / `admin123!`

---

# Bittada Marketplace Ecosystem

Modular, enterprise-grade B2B + B2C marketplace platform.
Source of truth: [`docs/TZ_EN.md`](TZ_EN.md) and [`docs/TZ_UZ.md`](TZ_UZ.md).

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12, Django 5, DRF, Channels |
| Async | Celery + Redis |
| DB | PostgreSQL 16 |
| Storage | S3 / MinIO |
| Frontend | Vanilla JS + Vite |
| Infra | Docker Compose (dev), Nginx, Gunicorn, Daphne |

## Quick start

```bash
Email: admin@bittada.uz
Parol: admin123
cp .env.example .env
make build
make up
make migrate
make superuser
```

The API is at `http://localhost:8000`, the frontend dev server at `http://localhost:5173`,
admin at `http://localhost:8000/admin`, MinIO console at `http://localhost:9001`.

## Layout

```
backend/   Django project + 24 modular apps
frontend/  Vite-based vanilla JS frontend
infra/     Docker, nginx, CI configs
docs/      TZ + architecture + API docs
```

Every Django app under `backend/apps/<name>/` follows the same skeleton:

```
models.py · serializers.py · views.py · urls.py · admin.py · permissions.py
services.py     # business logic (writes, transactions, side-effects)
selectors.py    # read-only queries (optimized querysets, no mutations)
tasks.py        # Celery async jobs
tests/          # pytest test modules
```

## Roadmap (phases)

See `docs/TZ_EN.md` §30. Current phase: **P0 — Foundation**.

## Contributing

- Conventional commits.
- `make lint`, `make fmt`, `make typecheck`, `make test` must pass before push.
- Migrations reviewed for safety (no destructive ops on big tables).
- Security-sensitive PRs need a second reviewer.
