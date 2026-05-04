# BITTADA MARKETPLACE ECOSYSTEM — TECHNICAL SPECIFICATION (TZ)

**Project Name:** Bittada
**Document Version:** 1.0 (Draft for Approval)
**Document Type:** Master Technical Specification
**Date:** 2026-04-27
**Owner:** Bittada Founders / Architecture Team
**Status:** Awaiting Stakeholder Approval

---

## 0. DOCUMENT PURPOSE

This document is the single source of truth for the design, scope, architecture, and acceptance criteria of the Bittada Marketplace Ecosystem.
Once approved, every implementation step (sprints, modules, code, infrastructure) MUST conform to this specification.
Any deviation requires a written change request and approval.

---

## 1. EXECUTIVE SUMMARY

Bittada is a modular, enterprise-grade B2B + B2C marketplace ecosystem covering:

- Standard retail products (B2C shopping)
- Manufactured goods with MOQ/MAX limits (B2B made-to-order)
- Services (specialists, designers, masters, contractors)
- 3D showrooms (GLB models)
- Multi-tenant warehouse and stock control
- Built-in escrow wallet (Upwork-style)
- Real-time chat with media exchange
- Dynamic CMS page builder (admin can create unlimited pages, sections, URLs)
- Public seller/supplier profiles
- Lead access via paid credit/point economy
- ERP/CRM integrations (Odoo, Bitrix24, 1C, MoySklad, Didox, custom)
- Multilingual content (UZ / RU / EN, extensible)
- Professional public REST API for mobile apps and partners

The platform must launch as a single deployable unit but be modular enough to split into independent microservers (frontend, backend, websocket, media, search) without rewriting code.

---

## 2. BUSINESS GOALS

| # | Goal | KPI |
|---|------|-----|
| G1 | Become the dominant marketplace in Uzbekistan for furniture/manufacturing | GMV / monthly orders |
| G2 | Replace fragmented seller workflows (Telegram, Instagram, manual invoices) | Active sellers with ≥10 orders/mo |
| G3 | Enable trustworthy B2B trade through escrow + verified profiles | Disputes resolved < 72h |
| G4 | Provide manufacturers with lead-generation via paid credits | ARPU per supplier |
| G5 | Be ERP-native for serious sellers (Odoo / 1C / Bitrix integration) | # of integrated accounts |
| G6 | Multilingual reach (UZ/RU/EN, expandable) | % non-UZ sessions |

---

## 3. NON-FUNCTIONAL REQUIREMENTS (PRIORITY ORDER)

1. **Security** — OWASP Top 10 hardened, brute-force protection, audit logs, encrypted secrets.
2. **Scalability** — Horizontal scaling, stateless API workers, queueable async tasks, read-replica friendly.
3. **UX** — Mobile-first, premium minimal corporate aesthetic, sub-200ms perceived navigation.
4. **Performance** — p95 API latency < 300ms; cached category/product pages < 100ms TTFB.
5. **SEO** — JSON-LD schema, server-side rendered metadata, sitemap.xml, robots.txt, canonical URLs.
6. **Maintainability** — Modular Django apps, business logic in services.py, query logic in selectors.py, ≥80% test coverage on critical paths.

---

## 4. TECH STACK (LOCKED)

### Backend
- **Language:** Python 3.12+
- **Framework:** Django 5.x + Django REST Framework
- **Async:** Django Channels (WebSocket), Celery + Redis (jobs)
- **DB:** PostgreSQL 16+ (single primary, read replicas later)
- **Cache:** Redis 7+
- **Auth:** JWT (rotation + blacklist), OAuth2 (Google, Telegram), Email OTP, Phone OTP

### Frontend
- **Language:** Vanilla JavaScript (ES2022+), HTML5, CSS3
- **Architecture:** Custom component system (no React/Vue dependency lock-in), reusable modules, dynamic builder
- **Build:** Vite for asset bundling, PostCSS, ESBuild
- **Responsive:** Mobile-first, breakpoints {sm 480, md 768, lg 1024, xl 1280, 2xl 1536}

### Storage
- S3-compatible object storage (AWS S3 or MinIO on-premise)
- Signed URLs for private files (blueprints, production files)
- Image pipeline: resize → WebP/AVIF → CDN

### Infrastructure
- **Web server:** Nginx (TLS termination, static, reverse proxy)
- **App server:** Gunicorn (sync) + Uvicorn/Daphne (ASGI for Channels)
- **Containerization:** Docker + Docker Compose (dev) → Kubernetes-ready manifests (prod future)
- **CI/CD:** GitHub Actions / GitLab CI — lint, test, build, deploy

### Search
- PostgreSQL full-text search at v1
- Migration path to Meilisearch / OpenSearch in v2

---

## 5. PROJECT FOLDER STRUCTURE

```
bittada/
├── backend/
│   ├── config/                    # Django project (settings, urls, asgi, wsgi)
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   ├── staging.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/                 # accounts, profiles, roles, permissions
│   │   ├── auth_methods/          # google, telegram, otp, login policies
│   │   ├── marketplace/           # cross-cutting marketplace logic
│   │   ├── products/              # standard + manufactured products
│   │   ├── services/              # service listings (specialists)
│   │   ├── categories/            # nested tree categories
│   │   ├── variants/              # color, size, custom attributes
│   │   ├── media/                 # images, GLB, video, file pipeline
│   │   ├── chat/                  # websocket chat, attachments
│   │   ├── orders/                # multi-stage order lifecycle
│   │   ├── escrow/                # wallet, hold, release, refund
│   │   ├── billing/               # credits, payments, invoices
│   │   ├── warehouse/             # multi-warehouse stock
│   │   ├── analytics/             # views, visitors, conversions
│   │   ├── pages/                 # CMS dynamic pages + sections
│   │   ├── seo/                   # metadata, sitemap, schema.org
│   │   ├── support/               # tickets, FAQ, forum, abuse
│   │   ├── blacklist/             # private fraud / scam list
│   │   ├── notifications/         # email, push, in-app, telegram
│   │   ├── api/                   # public REST API (versioned: /v1)
│   │   ├── integrations/          # Odoo, Bitrix24, 1C, MoySklad, Didox
│   │   ├── security/              # rate limit, IP block, audit log, device tracking
│   │   ├── i18n_extra/            # extra languages, AI text helpers
│   │   └── showroom/              # 3D GLB embeds, iframe pages
│   ├── core/                      # shared mixins, base models, utils, exceptions
│   ├── manage.py
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── dev.txt
│   │   └── prod.txt
│   ├── pyproject.toml
│   └── tests/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/            # header, footer, cards, modals, drawer, chat-widget
│   │   ├── pages/                 # home, product, profile, dashboard, etc.
│   │   ├── modules/               # cart, wishlist, search, auth flows
│   │   ├── builder/               # CMS section renderer (hero, banner, slider...)
│   │   ├── styles/
│   │   ├── utils/
│   │   ├── api/
│   │   └── main.js
│   └── vite.config.js
├── infra/
│   ├── docker/
│   │   ├── nginx/
│   │   ├── backend.Dockerfile
│   │   ├── frontend.Dockerfile
│   │   └── compose.yml
│   ├── k8s/                       # future
│   └── ci/
├── docs/
│   ├── TZ_EN.md (this document)
│   ├── TZ_UZ.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DB_SCHEMA.md
│   └── CHANGELOG.md
└── scripts/
```

Each Django app MUST contain:
`models.py · serializers.py · views.py · urls.py · services.py · selectors.py · tasks.py · admin.py · permissions.py · tests/`

- **services.py** — business logic (write side, side-effects, transactions)
- **selectors.py** — read queries (no mutations, optimized querysets)
- **tasks.py** — Celery async jobs

---

## 6. ROLES & PERMISSIONS

### 6.1 Role Hierarchy

| Role | Description | Public Profile | Can Sell | Can Buy | Admin Panel |
|------|-------------|----------------|----------|---------|-------------|
| `customer` | End buyer, individual or company | ❌ | ❌ | ✅ | ❌ |
| `seller` | External seller / manufacturer / specialist | ✅ | ✅ | ✅ | Limited (own data) |
| `internal_supplier` | Bittada-owned supplier accounts | ✅ | ✅ | ✅ | Limited |
| `admin` | Bittada staff (moderation, support, content) | ❌ | ❌ | ❌ | ✅ scoped |
| `super_admin` | Top-level platform owner | ❌ | ❌ | ❌ | ✅ full |

### 6.2 Account Type (orthogonal to role)

- `individual` — natural person, basic KYC
- `company` — legal entity, requires registration docs, stamp/certificates

### 6.3 Seller Sub-Categories (parent classification)

A seller chooses one or more profession parents at registration:

- `supplier` (yetkazib beruvchi)
- `manufacturer` (ishlab chiqaruvchi)
- `master` (usta — handcrafter, installer, repair)
- `designer` (interior, product, graphic)

Each sub-category exposes additional profile fields (portfolio, certifications, working hours).

### 6.4 Permission Matrix

- Default permissions per role are seeded.
- Super Admin can edit/extend permissions per role and per individual user.
- Granularity: object-level (e.g., "can_edit_only_own_products"), action-level (CRUD), and field-level (e.g., hide cost price).
- Implemented via Django Guardian or a custom permission table — decision logged in `ARCHITECTURE.md`.

### 6.5 Profile Visibility Rules

- `customer` → no public page, no `/u/{username}/` route exists.
- `seller` / `internal_supplier` → public page enabled by default; user may toggle public/private.
- Private profile → only logged-in users with prior chat history can see.

---

## 7. USER PROFILE SPECIFICATION

### Editable by user:
- account_type (individual / company)
- first_name, last_name (or company_name)
- username (unique, slugified, used in URL `/u/{username}`)
- avatar — gallery up to 6 images, one marked primary
- cover image
- bio (rich text, multilingual UZ/RU/EN)
- phones (list, each phone has visibility flag: public / paid-reveal / private)
- email (same visibility flags)
- telegram handle
- website
- address (text + geo coordinates)
- working hours (per weekday)
- documents (KYC) — uploaded, admin-verified
- profession parents (supplier / manufacturer / master / designer — multi-select)

### System-managed:
- rating (0.0 – 5.0, computed from reviews)
- review_count
- verified status (by admin)
- joined_at
- last_seen
- profile_views (lifetime)
- visitor log (admin/seller can view who visited and when)

### Privacy controls:
- Toggle visibility of phones, email, address (public / paid-reveal / hidden)
- Block specific users
- Public-page master switch (on/off, only sellers)

---

## 8. AUTHENTICATION & REGISTRATION

### 8.1 Methods (admin-toggleable)

1. Google OAuth2
2. Email + password + OTP confirmation
3. Phone number + SMS OTP
4. Telegram Login Widget

Each method is enabled/disabled from Super Admin panel without code change.

### 8.2 Security

- **Rate limit:** 5 failed login attempts → temporary lock (15 min) → escalating to IP block.
- **Device tracking:** every login records IP, user-agent, geo-IP; user can view/revoke sessions.
- **JWT rotation:** access token (15 min) + refresh token (14 days, rotating + blacklist on use).
- **Password policy:** min 10 chars, 1 number, 1 symbol; bcrypt/argon2 hashing.
- **2FA optional:** TOTP for sellers and admins (mandatory for admin/super_admin).

### 8.3 Audit log

Every auth event (login, logout, password change, role change, OAuth bind) is written to `security.audit_log` with full context (actor, target, ip, ua, before/after).

---

## 9. DYNAMIC CMS PAGE BUILDER

### 9.1 Capability

Admins can create UNLIMITED static/CMS pages with custom URL slugs. Examples:
- `/about`
- `/contact`
- `/services`
- `/furniture`
- `/manufacturers/tashkent`

### 9.2 Page Fields

- `title` (multilingual)
- `slug` / full URL path (validated, unique, hierarchical via parent_page)
- `parent_page` (nullable) → enables nested URLs (`/services/installation`)
- `permission` (public / authenticated / role-restricted)
- `visibility` (draft / scheduled / published / archived)
- `seo_title`, `seo_description`, `seo_keywords`, `og_image`, `canonical_url`, `noindex` flag
- `template` (default / landing / docs / form)
- `header_variant`, `footer_variant`
- `custom_css`, `custom_js` (sandboxed, super_admin only)

### 9.3 Section Types (drag-drop)

- Hero block (image/video bg, headline, CTA)
- Banner
- Plain text
- Rich text (TipTap / ProseMirror style editor)
- Product slider (filter by category/tag)
- Service slider
- Category grid
- FAQ accordion
- Image gallery
- Video embed
- 3D model embed (GLB)
- Custom HTML / CSS / JS block (sandboxed iframe)
- Call-to-action button
- Testimonials
- Form (lead capture, integrates with CRM)

### 9.4 Section Permissions

Each section can have its own visibility: public / role-restricted / hidden. Allows e.g. "wholesale prices" section visible only to verified sellers.

### 9.5 Versioning

- Every page edit creates a revision (autosaved).
- Admin can roll back to any revision.

---

## 10. PRODUCT MODULE

### 10.1 Product Types

1. `standard` — physical product, sold per unit, appears in `/shop`
2. `manufacturing` — made-to-order, has MOQ + MAX limits, price range
3. `service` — appears in `/services`, time-based or scope-based (separate UI)

### 10.2 Common Fields

- `title` (multilingual UZ/RU/EN, AI-assist for description generation)
- `description` (rich text, multilingual)
- `category` (FK to nested tree)
- `subcategory_path` (denormalized for fast filter)
- `sku` (auto or manual)
- `uuid` (immutable public id)
- `hashtags` (free-text, comma-separated, indexed for search)
- `tags` (curated tags, FK)
- `price` (current)
- `old_price` (strike-through)
- `min_price` / `max_price` (manufacturing only — range)
- `discount_percent`, `discount_start`, `discount_end`, `discount_quantity` (per-quantity tier)
- `stock_qty` (standard) — sourced from warehouse module
- `moq` minimum order quantity (manufacturing)
- `max_qty` per single order
- `variants`: color, size, material — open attribute schema
- `images` (max 10, ordered, alt text per locale)
- `video` (single, optional)
- `glb_models` (multiple — primary + variants like color)
- `downloadable_files` (public — anyone can download)
- `production_files` (private — request-to-access flow)
- `blueprint_files` (private — request-to-access flow)
- `visibility_rules` per file/group (public / on-request / paid)

### 10.3 Private File Access Flow

When a user requests access to a private file:
1. Owner gets notification (in-app, email, telegram).
2. Notification includes requester profile, IP, device, location, message.
3. Owner can: approve / deny / approve-once-paid (price set).
4. All actions logged in audit trail.

### 10.4 Discounts

- Percentage or fixed amount
- Time-bound (start/end)
- Quantity-tier additional discount (e.g., +5% if qty ≥ 50)
- Stackable rules with explicit precedence (admin-defined)

### 10.5 Product Analytics (per product)

- Total views (unique + total)
- Visitor list (who viewed, when, from where) — visible to product owner
- Add-to-cart count
- Wishlist count
- Contact-click count
- Order conversion rate
- Daily / weekly / monthly chart
- Source breakdown (organic, internal search, ads, referral)

---

## 11. SERVICES MODULE

Services have a distinct UI from products:

- Booking-style listing
- Provider availability calendar
- Status timeline visible to client (in queue / scheduled / in progress / completed / canceled)
- Live progress feed: provider can post updates, photos, "currently working at: location"
- Open vs closed status visible to public (so clients see what is in-progress vs taking new orders)
- Payment via escrow

---

## 12. CATEGORY SYSTEM

- Infinite nested tree (Materialized Path or MPTT)
- Created/edited only by admin / super_admin
- Per-category fields:
  - name (multilingual)
  - icon (svg/png)
  - cover image
  - SEO metadata (title, description, og_image)
  - visibility / status
  - product type filter (standard / manufacturing / service / mixed)
  - permission (public / role-restricted)
- Each category page has its own SEO and optional CMS sections (mini landing page per category).

---

## 13. CHAT SYSTEM

- Real-time via Django Channels (WebSocket).
- Fallback to long-poll for restricted networks.
- Message types:
  - text
  - emoji
  - image (with thumbnail)
  - file (any type, virus-scanned)
  - video
  - voice message (browser MediaRecorder)
  - location (geo coordinates + map preview)
  - quote (link to product/order)
- Read receipts, typing indicator, online/last-seen.
- Order-linked chat: when an inquiry/order exists, chat thread is tied to it.
- Moderation: admin can read/freeze flagged threads (with audit log).
- Encryption at rest for media; signed URLs for retrieval.

---

## 14. ORDER SYSTEM (MULTI-STAGE LIFECYCLE)

| # | Stage | Notes |
|---|-------|-------|
| 1 | Inquiry | Customer asks question, no commitment |
| 2 | Offer | Seller posts a formal offer (price, terms, lead time) |
| 3 | Negotiation | Counter-offers, chat-driven |
| 4 | Escrow Payment | Funds held in Bittada wallet |
| 5 | Started | Production / fulfillment begins |
| 6 | Production | (manufacturing only) milestones, photos, ETA |
| 7 | Shipping | Courier integration, tracking number |
| 8 | Delivered | Buyer confirms |
| 9 | Completed | Escrow released to seller |
| 10 | Reviewed | Buyer leaves rating & review |

- Disputes can be opened at any stage from #4 onwards.
- Each stage transition is logged with actor, timestamp, reason.
- Sellers see who carted / inquired / ordered (privacy-respecting where appropriate).

---

## 15. ESCROW & WALLET (Upwork-style)

- Each user has a wallet with two ledgers:
  - `available_balance` — withdrawable
  - `escrow_balance` — held for active orders
- Buyer deposits → funds move to `escrow_balance` against a specific order.
- On order completion → funds move to seller's `available_balance` (minus platform commission).
- On dispute → admin arbitration releases / refunds proportionally.
- Withdrawal requests → manual or automatic (per partner bank rules).
- All transactions are immutable rows in `escrow.transaction_log` (double-entry bookkeeping).
- Sellers can also act as buyers and place orders to other suppliers — same wallet.

---

## 16. CREDITS / POINTS ECONOMY

Credits gate paid actions:

| Action | Default cost (configurable) |
|--------|----------------------------|
| Reveal seller phone | 1 credit |
| Reveal seller email | 1 credit |
| Open chat (initiate) | 2 credits |
| Priority lead access | 5 credits |
| Boosted listing (24h) | 20 credits |

- Credits purchasable via payment gateway (Click, Payme, Uzcard, Visa, crypto-ready).
- Sellers see analytics: who viewed contact, who unlocked, conversion to order.
- "Contact unlock" page is a separate, deliberate UI step → no accidental charge.
- Each contact unlock is logged and visible to seller as a lead.

---

## 17. WAREHOUSE & STOCK

- Multi-warehouse per seller:
  - `home` (own residence / shop)
  - `external` (rented warehouse)
  - `supplier` (drop-ship from upstream supplier)
- Stock statuses per SKU per warehouse: `available`, `reserved`, `out_of_stock`, `incoming`.
- Reservations created on order; released on cancel/refund.
- Geo coordinates per warehouse for distance-aware delivery quotes.
- ERP sync (Odoo / 1C / MoySklad) reconciles stock periodically.

---

## 18. ANALYTICS

### 18.1 Seller Dashboard
- Product views (per product, per day)
- Profile views (visitor list)
- Source breakdown (search / social / direct / referral)
- Add-to-cart count, contact clicks, conversion rate
- Order pipeline (inquiry → completed funnel)
- Revenue charts (D / W / M / Y)
- Top products, slow movers
- Lead spend (credits used) vs orders won

### 18.2 Admin Dashboard
- GMV, take rate, active sellers, active customers
- Cohort retention
- Top categories, top regions
- Fraud signals (multi-account, IP collisions)

---

## 19. BLACKLIST (Private B2B Trust Module)

- Visible only to roles: `seller`, `internal_supplier`, `admin`, `super_admin`.
- Customers and the public CANNOT see it.
- Entry types: `fraud_buyer`, `unpaid_buyer`, `scam_supplier`, `abuse`, `harassment`.
- Each entry: target user/phone/email, reason, evidence (files/screenshots), reporter, date, status (pending / verified / disputed / cleared).
- Admin moderates entries; sellers vote on credibility; persistent disputes hide the entry.

---

## 20. 3D SHOWROOM (GLB Module)

- Every product can attach multiple GLB models (per color/variant).
- Public iframe-embed page per product GLB: `/embed/glb/{product_uuid}/{variant_id}`.
- Category-level showroom: `/showroom/{category_slug}` lists only products with GLB.
- Sharable embed code generator (copy-paste iframe HTML).
- Mobile AR view via `<model-viewer>` web component.

---

## 21. SUPPORT CENTER

- **Ticket system:** open / in_progress / resolved / closed; priority levels; SLA timer.
- **FAQ:** admin-curated, multilingual, searchable.
- **Forum:** community Q&A with upvotes; moderated.
- **Abuse reports:** product complaints, user complaints, content takedown.
- **Image attachments** on every ticket and report.
- **Admin response templates** (canned replies).
- **Internal notes** (visible to staff only).

---

## 22. SEO

For every entity (page, product, profile, category):
- `meta_title`, `meta_description`, `keywords`
- Open Graph tags (`og:title`, `og:description`, `og:image`, `og:type`)
- Twitter card
- `canonical` URL
- JSON-LD schema (Product, Service, Organization, BreadcrumbList, Review, FAQPage)
- Auto-generated `sitemap.xml` (segmented by entity type, paginated)
- `robots.txt` admin-editable
- Slug rules: lowercase, hyphenated, multilingual transliteration safe
- 301 redirects on slug change (admin-managed redirect table)
- AMP NOT required at v1.

---

## 23. MULTILINGUAL

- Default languages: **Uzbek (uz)**, **Russian (ru)**, **English (en)**.
- Super Admin can add more languages dynamically (DB-backed, no code change).
- All user-facing strings stored as translatable rows; UI uses Django i18n (`gettext`) for static + a translation table for dynamic.
- Product creation form requires all 3 default languages (configurable: required / optional per language).
- AI-assisted text generation for descriptions: takes draft text, returns polished translations in selected languages (via OpenAI/Claude API, configurable provider).
- Language switcher in header; selection persisted per user and via cookie for guests.

---

## 24. ERP / CRM INTEGRATIONS

Pre-built connectors (admin enables per seller account):
- **Odoo** (REST + XML-RPC)
- **Bitrix24** (REST)
- **1C** (file exchange + REST adapter)
- **MoySklad** (REST)
- **Didox** (e-invoice / EDI for Uzbekistan)
- **Custom** webhook + REST template

Sync targets:
- Stock levels (bidirectional)
- Orders (Bittada → ERP)
- Customers (Bittada → CRM)
- Invoices (ERP → Bittada for display)
- Product catalog (ERP → Bittada or vice versa, per integration setting)

---

## 25. PUBLIC API

- Versioned: `/api/v1/...`
- Auth: JWT bearer or API token (per integration).
- Rate limited per token (configurable tiers).
- OpenAPI 3 spec auto-generated, hosted at `/api/docs`.
- Webhooks: subscribable events (order.created, order.completed, stock.changed, message.received) with HMAC-signed payloads.
- Designed for: mobile apps (iOS / Android), partner ERPs, courier integrations, external storefronts.

---

## 26. SECURITY (MANDATORY)

| Control | Requirement |
|---------|-------------|
| CSRF | Django CSRF middleware on all session views |
| XSS | Auto-escape templates; CSP header strict; sanitize rich text on save |
| SQLi | ORM only; no raw SQL with user input; parameterized when raw needed |
| Rate limit | DRF throttling + Redis counter; per-IP + per-user |
| IP block | Manual + automatic (failed login, abusive patterns) |
| Brute-force | 5 fails → 15 min lock → escalate to IP block |
| Device tracking | Per-session record with revoke ability |
| Audit logs | All admin actions, role changes, financial events |
| Permission matrix | Object-level + field-level enforcement |
| Secure headers | HSTS, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy strict-origin-when-cross-origin, Permissions-Policy minimal |
| File validation | MIME sniff + extension whitelist; image re-encode; ClamAV scan for non-images |
| JWT | Short-lived access + rotating refresh + blacklist on logout |
| Session control | List + revoke; force re-auth on sensitive ops |
| Secrets | `.env` only, never in git; vault-ready |
| Data at rest | Encrypted media buckets; PII column-level encryption for KYC docs |
| GDPR-style | Account deletion + data export endpoints |

---

## 27. UI / UX STANDARDS

### Style
- Minimal, premium, corporate
- Generous whitespace
- Mobile-first responsive
- Subtle, intentional animations (≤ 200ms, no jank)

### Header (sticky)
- Logo
- Mega menu (categories)
- Universal search (products, services, sellers, hashtags)
- Language switcher
- Login / register
- Favorites
- Cart
- Notifications bell
- Dashboard entry (role-aware)

### Footer (dynamic)
- About
- Contacts
- Policies (terms, privacy, refund)
- Help center
- Social links
- App download links
- Newsletter signup
- Language switch (mirror)

Header & footer are CMS-editable (sections, links, banners) — same builder as pages.

---

## 28. DEPLOYMENT & FUTURE SPLIT

### v1 (single host)
- Docker Compose with: nginx, backend (gunicorn), channels (daphne), postgres, redis, celery worker, celery beat, minio.

### v2 (split-ready, no code change)
- frontend server (static + edge cache)
- backend server (REST API)
- websocket server (Channels)
- media server (S3 / MinIO)
- search server (Meilisearch)
- worker pool (Celery)

All inter-service traffic via signed JWT; no shared filesystem.

---

## 29. CODE QUALITY RULES

- Type hints everywhere (Python 3.12 typing).
- Lint: `ruff` + `black` + `mypy --strict` on critical apps.
- Tests: `pytest` with coverage gates per app (≥ 80% on services + selectors).
- Comments only where the WHY is non-obvious. Avoid restating WHAT.
- Conventional commits.
- PR checklist: tests, migration safety, docs, security review.

---

## 30. ROADMAP (PHASED DELIVERY)

| Phase | Scope | Outcome |
|-------|-------|---------|
| **P0 — Foundation** | Repo skeleton, settings, auth, users, RBAC, admin, CI, base UI shell | Loginable platform, header/footer, empty pages |
| **P1 — Catalog Core** | Categories, products (standard), media pipeline, search, product page, category page | Browsable catalog |
| **P2 — Profiles & Chat** | Public seller profiles, chat (WebSocket), profile editor | Buyer-seller communication |
| **P3 — Orders & Escrow** | Cart, checkout, order lifecycle, escrow wallet, payments | First end-to-end transaction |
| **P4 — Manufacturing & Services** | Manufactured products (MOQ/range), services module, booking timeline | B2B made-to-order live |
| **P5 — CMS Builder** | Dynamic pages, sections, header/footer builder, SEO fields | Content team self-serve |
| **P6 — 3D & Files** | GLB embeds, blueprint request flow, showroom pages | 3D-first commerce |
| **P7 — Credits & Analytics** | Credit economy, contact unlock, seller analytics, admin analytics | Monetized leads |
| **P8 — Integrations** | Odoo, Bitrix24, 1C, MoySklad, Didox, public API, webhooks | ERP-grade sellers |
| **P9 — Multilingual & AI text** | UZ/RU/EN required, AI helper, language admin | International-ready |
| **P10 — Hardening** | Security audit, load test, SEO audit, accessibility audit, launch | GA |

---

## 31. ACCEPTANCE CRITERIA (per phase, summarised)

- All endpoints documented in OpenAPI.
- All apps have `services.py` + `selectors.py` + tests.
- p95 latency budget met under load test (1000 RPS sustained).
- OWASP ZAP scan: zero high/critical.
- Lighthouse: Performance ≥ 90, Accessibility ≥ 95, SEO ≥ 95 on top 10 pages.
- All admin-configurable items configurable WITHOUT code change.
- CI green; staging matches prod schema.

---

## 32. OUT OF SCOPE (v1)

- Native mobile apps (only API-ready).
- Crypto payments (API hooks only).
- Live video streaming.
- Auctions.
- Subscription products (recurring billing).
- Marketplace ads / sponsored placements (beyond credit-boost).

---

## 33. GLOSSARY

- **MOQ** — Minimum Order Quantity.
- **GMV** — Gross Merchandise Value.
- **Escrow** — Funds held by platform until conditions met.
- **GLB** — Binary glTF, 3D model format.
- **ERP** — Enterprise Resource Planning.
- **CMS** — Content Management System.
- **KYC** — Know Your Customer (identity verification).

---

## 34. APPROVAL

This document requires sign-off from:
- [ ] Founder / Product Owner
- [ ] Tech Lead
- [ ] Security Lead
- [ ] UX Lead

After sign-off, work proceeds in the order defined in §30. Any change must be logged in `docs/CHANGELOG.md` and reviewed by the Tech Lead.

---

**END OF DOCUMENT — TZ_EN.md v1.0**
