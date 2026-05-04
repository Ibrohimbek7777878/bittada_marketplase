# Development guide

## First-time setup

```bash
cp .env.example .env
make build
make up
make migrate
make superuser
```

- API:      http://localhost:8000
- Admin:    http://localhost:8000/admin
- API docs: http://localhost:8000/api/docs/
- Frontend: http://localhost:5173 (run `make frontend-dev` on the host)
- MinIO:    http://localhost:9001 (login uses `S3_ACCESS_KEY` / `S3_SECRET_KEY`)

## Daily commands

| Command | What it does |
|---------|--------------|
| `make up` / `make down` | Bring stack up / down |
| `make logs` | Tail container logs |
| `make migrate` | Apply DB migrations |
| `make makemigrations` | Generate new migrations from model changes |
| `make test` | Run pytest |
| `make lint` / `make fmt` | Lint and auto-fix |
| `make typecheck` | Run mypy |
| `make shell` | Django shell in backend container |
| `make frontend-dev` | Run Vite dev server on host |

## Adding a new app

1. Create directory under `backend/apps/<name>/` with the standard files
   (copy the skeleton from any existing app).
2. Add `"apps.<name>"` to `LOCAL_APPS` in `backend/config/settings/base.py`.
3. Mount its URLs at `/api/v1/<name>/` in `backend/config/urls.py`.
4. Run `make makemigrations` and `make migrate`.

## Adding a model

1. Inherit from `core.models.BaseModel` (or `AuditableModel` for sensitive
   domains).
2. Place write logic in `services.py`, read queries in `selectors.py`.
3. Register the model in `admin.py` for super admin visibility.
4. Add tests under `tests/`.

## Migration safety

- Never drop/rename a column on a >1M row table without a multi-step plan
  (add new column → backfill → switch reads → drop old column in a separate release).
- Use `pgtrigger` for invariants instead of app-level locks where possible.

## Code style

- `ruff` + `black` enforce style.
- `mypy --strict` on `apps/` and `core/`.
- Type hints required.
- Comments explain WHY (non-obvious constraints), not WHAT.

## Testing rules

- Per-app tests live in `apps/<name>/tests/`.
- Database tests use `pytest.mark.django_db` (the marker auto-applies via
  `--reuse-db` in `pyproject.toml`).
- Slow tests get `@pytest.mark.slow`.
- Aim for ≥ 80 % coverage on `services` + `selectors`.
