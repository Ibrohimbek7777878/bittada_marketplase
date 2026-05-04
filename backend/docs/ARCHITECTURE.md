# Bittada — Architecture

Living document. Update when a meaningful boundary changes.

## Layered structure (per Django app)

```
apps/<name>/
  models.py        # ORM rows
  serializers.py   # DRF input/output shapes
  views.py         # HTTP endpoints (thin: parse → call service → serialise)
  urls.py          # routes
  permissions.py   # DRF permission classes
  services.py      # WRITE-side business logic, transactional, side-effects
  selectors.py     # READ-side queries, no mutation
  tasks.py         # Celery async jobs
  admin.py         # Django admin
  tests/           # pytest
```

Rule of thumb:
- Views never call ORM directly. They go through `services.*` or `selectors.*`.
- Services raise `core.exceptions.DomainError` on rule violations.
- Selectors return querysets / dicts; never mutate.

## Cross-app contracts

| From | To | Mechanism |
|------|----|-----------|
| `auth_methods` | `users` | Calls `users.services.create_user_with_profile` |
| `security` middleware | request | Adds `request.bittada` (ip, ua, started_at) |
| `axes` lockout | `security.services.on_axes_lockout` | Wired in settings |
| `chat` (P2) | `orders` | Order chat threads keyed by order id |
| `escrow` | `users` wallet | One-to-one via `user.wallet` (P3) |

## Data identifiers

- `User.id` — UUID, public.
- `User.email` — login id, lower-cased, unique.
- `User.username` — public handle, used in `/u/{username}/`.
- All BaseModel rows use UUID PKs to prevent enumeration.

## Async + realtime

- WSGI (gunicorn) serves HTTP `/api`.
- ASGI (daphne) serves WebSocket `/ws`.
- Celery worker runs out-of-band tasks (OTP delivery, notifications, scheduled cleanups).
- Celery beat schedules periodic jobs (e.g. `auth.cleanup_expired_otps`).

## Storage

- DB: PostgreSQL 16. Single primary at v1, replicas later.
- Cache + channels + Celery: Redis (separate logical DBs 0/1/2/3).
- Object storage: S3 / MinIO. Two buckets:
  - `bittada-public` (avatars, product images served directly)
  - `bittada-private` (KYC docs, blueprints — signed URLs only)

## Security baseline

- Argon2 password hashing.
- `django-axes` with 5/15min lockout, repeat-offender → 6h IP block.
- DRF throttling: `anon` 60/min, `user` 300/min, `auth` 10/min.
- All admin / financial actions go to `security.AuditLog` (append-only).
- HSTS, X-Frame-Options DENY, strict referrer, COOP same-origin.

## What's not here yet

P0 ships the foundation. Heavier modules (catalog, chat, escrow, CMS pages,
3D showroom, ERP integrations) are scaffolded as empty apps and built per
the roadmap in `TZ_EN.md` §30.
