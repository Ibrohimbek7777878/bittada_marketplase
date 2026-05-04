# Changelog

All notable changes to Bittada are recorded here. Conventional sections.

## [Unreleased] — P0 Foundation (2026-04-27)

### Added
- Initial monorepo: `backend/`, `frontend/`, `infra/`, `docs/`.
- Django 5 project with split settings (`base/dev/staging/prod`).
- 24 modular apps scaffolded with the standard skeleton
  (`models · serializers · views · urls · services · selectors · tasks · admin · permissions · tests`).
- Core shared layer: `BaseModel`, `SoftDeleteModel`, `AuditableModel`,
  `DomainError` family, `DefaultPagination`, role-based permission classes,
  JSON log formatter.
- Users domain: custom `User` (UUID, email login, username handle, 5 roles,
  individual/company), `Profile`, `ProfileAvatar`, `KycDocument`,
  `PermissionGrant`. Public profile only for sellers.
- Auth methods: email+password registration, JWT (rotating refresh + blacklist),
  email/phone OTP scaffold, Google + Telegram social-login scaffold,
  `AuthMethodConfig` for admin-toggleable methods.
- Security: `IpBlock`, `AuditLog`, `RequestLog`, `IPBlockMiddleware`,
  `RequestContextMiddleware`, axes lockout escalation to IP block.
- Docker stack: postgres, redis, minio, backend (gunicorn), channels (daphne),
  celery worker + beat, nginx reverse proxy.
- Frontend Vite scaffold: vanilla JS components (header, footer,
  language switcher), tokens-based design system, i18n helper (UZ/RU/EN),
  thin API client, home page placeholder.
- CI workflow (lint, type-check soft-fail, tests, frontend build).
- TZ documents in English and Uzbek.

### Known gaps (P1+)
- Catalog (categories, products, services).
- Real-time chat consumers.
- Escrow wallet, orders, payments.
- CMS page builder.
- 3D showroom embeds.
- ERP/CRM integrations.
- Public REST API surface beyond auth/users.
