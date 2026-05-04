# BITTADA MARKETPLACE EKOSISTEMASI — TEXNIK TOPSHIRIQ (TZ)

**Loyiha nomi:** Bittada
**Hujjat versiyasi:** 1.0 (Tasdiqlash uchun loyiha)
**Hujjat turi:** Asosiy texnik topshiriq (Master TZ)
**Sana:** 2026-04-27
**Mas'ul:** Bittada Asoschilari / Arxitektura jamoasi
**Holati:** Buyurtmachi tasdig'ini kutmoqda

---

## 0. HUJJAT MAQSADI

Bu hujjat — Bittada marketplace ekotizimini loyihalash, qamrov, arxitektura va qabul qilish mezonlari bo'yicha YAGONA HAQIQAT MANBAYI.
Tasdiqlangandan so'ng har qanday ishlab chiqish bosqichi (sprintlar, modullar, kod, infratuzilma) ushbu TZ ga MAJBURIY ravishda mos kelishi kerak.
Har qanday chetlanish yozma o'zgartirish so'rovi va tasdiq talab qiladi.

---

## 1. QISQACHA TUSHUNTIRISH
  
Bittada — bu modulli, korporativ darajadagi B2B + B2C marketplace ekotizimi bo'lib, quyidagilarni qamrab oladi:

- Standart chakana mahsulotlar (B2C — shopping)
- Buyurtma asosida ishlab chiqariladigan mahsulotlar (MOQ + MAX bilan B2B)
- Xizmatlar (mutaxassislar, dizaynerlar, ustalar, pudratchilar)
- 3D showroom (GLB modellar)
- Ko'p omborli zaxira boshqaruvi                                                                                                                                                                                                                                        
- Ichki escrow hamyon (Upwork uslubidagi)
- Real-time chat (matn, rasm, video, fayl, lokatsiya)
- Dinamik CMS sahifa quruvchi (admin cheksiz sahifa, URL, bo'lim yarata oladi)
- Sotuvchi/yetkazib beruvchining ommaviy profili
- Pullik kredit/ball iqtisodiyoti orqali aloqa ochish
- ERP/CRM integratsiyalari (Odoo, Bitrix24, 1C, MoySklad, Didox, custom)
- Ko'p tilli kontent (UZ / RU / EN, kengaytiriladigan)
- Mobil ilovalar va hamkorlar uchun professional ochiq REST API

Platforma yagona deploy birligi sifatida ishga tushishi, lekin keyinchalik mustaqil mikroserverlarga (frontend, backend, websocket, media, search) — kodga teginmasdan — ajratilishi mumkin bo'lishi kerak.

---                                                                                                                                                       

## 2. BIZNES MAQSADLAR

| # | Maqsad | KPI |
|---|--------|-----|
| G1 | O'zbekistonda mebel/ishlab chiqarish bo'yicha №1 marketplace bo'lish | GMV / oylik buyurtmalar |
| G2 | Bo'lakka ajralgan sotuvchi oqimlarini (Telegram, Instagram, qo'lda invoice) almashtirish | Oyiga ≥10 buyurtma qilgan faol sotuvchi |
| G3 | Escrow + tasdiqlangan profillar orqali ishonchli B2B savdo | Nizolarni 72 soatdan oldin hal qilish |
| G4 | Ishlab chiqaruvchilarga pullik kreditlar orqali lid berish | Ta'minotchi ARPU |
| G5 | Jiddiy sotuvchilar uchun ERP-native (Odoo / 1C / Bitrix integratsiyasi) | Integratsiyali akkauntlar soni |
| G6 | Ko'p tilli qamrov (UZ/RU/EN, kengaytiriladigan) | Non-UZ sessiyalar % |

---

## 3. NOFUNKSIONAL TALABLAR (USTUVORLIK BO'YICHA)

1. **Xavfsizlik** — OWASP Top 10 himoyasi, brute-force himoya, audit jurnal, sirlar shifrlangan.
2. **Masshtablashuv** — Gorizontal masshtablash, stateless API workerlar, async navbat, read-replica do'st.
3. **UX** — Mobile-first, premium minimalistik korporativ uslub, 200ms dan kam navigatsiya hissi.
4. **Tezlik** — p95 API kechikish < 300ms; kategoriya/mahsulot sahifalari < 100ms TTFB.
5. **SEO** — JSON-LD schema, server-tomon meta, sitemap.xml, robots.txt, canonical URL.
6. **Qo'llab-quvvatlanuvchanlik** — Modulli Django ilovalar, biznes-mantiq `services.py` da, query-mantiq `selectors.py` da, kritik yo'llarda ≥80% test qoplama.

---

## 4. TEXNOLOGIK STACK (QAT'IY)

### Backend
- **Til:** Python 3.12+
- **Framework:** Django 5.x + Django REST Framework
- **Async:** Django Channels (WebSocket), Celery + Redis (vazifalar)
- **DB:** PostgreSQL 16+ (asosiy + keyinchalik read replica)
- **Cache:** Redis 7+
- **Auth:** JWT (rotation + blacklist), OAuth2 (Google, Telegram), Email OTP, Phone OTP

### Frontend
- **Til:** Vanilla JavaScript (ES2022+), HTML5, CSS3
- **Arxitektura:** O'z komponent tizimi (React/Vue ga bog'lanmaslik), qayta ishlatiluvchi modullar, dinamik builder
- **Build:** Vite (asset bundling), PostCSS, ESBuild
- **Responsive:** Mobile-first, breakpointlar {sm 480, md 768, lg 1024, xl 1280, 2xl 1536}

### Saqlash
- S3 ga mos object storage (AWS S3 yoki MinIO o'z serverida)
- Yopiq fayllar uchun signed URL (chizmalar, ishlab chiqarish fayllari)
- Rasm pipeline: o'lchamini o'zgartirish → WebP/AVIF → CDN

### Infratuzilma
- **Web server:** Nginx (TLS, statik, reverse proxy)
- **App server:** Gunicorn (sync) + Uvicorn/Daphne (ASGI Channels uchun)
- **Konteynerlash:** Docker + Docker Compose (dev) → Kubernetes manifestlari (kelajakdagi prod)
- **CI/CD:** GitHub Actions / GitLab CI — lint, test, build, deploy

### Qidiruv
- v1 da PostgreSQL full-text search
- v2 da Meilisearch / OpenSearch ga o'tish

---

## 5. LOYIHA PAPKA TUZILISHI

```n
bittada/
├── backend/
│   ├── config/                    # Django loyiha (settings, urls, asgi, wsgi)
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   ├── staging.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/                 # akkauntlar, profillar, rollar, ruxsatlar
│   │   ├── auth_methods/          # google, telegram, otp, login siyosatlari
│   │   ├── marketplace/           # umumiy marketplace mantiqi
│   │   ├── products/              # standart va ishlab chiqariladigan mahsulotlar
│   │   ├── services/              # xizmatlar (mutaxassislar)
│   │   ├── categories/            # daraxt shaklidagi kategoriyalar
│   │   ├── variants/              # rang, o'lcham, atributlar
│   │   ├── media/                 # rasm, GLB, video, fayl quvuri
│   │   ├── chat/                  # websocket chat, biriktiriladigan fayllar
│   │   ├── orders/                # ko'p bosqichli buyurtma sikli
│   │   ├── escrow/                # hamyon, hold, release, refund
│   │   ├── billing/               # kreditlar, to'lovlar, hisob-fakturalar
│   │   ├── warehouse/             # ko'p omborli zaxira
│   │   ├── analytics/             # ko'rishlar, tashrifchilar, konversiyalar
│   │   ├── pages/                 # CMS dinamik sahifalar + bo'limlar
│   │   ├── seo/                   # meta, sitemap, schema.org
│   │   ├── support/               # tikets, FAQ, forum, shikoyat
│   │   ├── blacklist/             # yopiq fraud / scam ro'yxati
│   │   ├── notifications/         # email, push, in-app, telegram
│   │   ├── api/                   # ochiq REST API (versionli: /v1)
│   │   ├── integrations/          # Odoo, Bitrix24, 1C, MoySklad, Didox
│   │   ├── security/              # rate limit, IP block, audit log, qurilma kuzatuvi
│   │   ├── i18n_extra/            # qo'shimcha tillar, AI matn yordamchilari
│   │   └── showroom/              # 3D GLB embed, iframe sahifalari
│   ├── core/                      # umumiy mixinlar, base modellar, util
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
│   │   ├── components/            # header, footer, kartochkalar, modal, drawer, chat
│   │   ├── pages/                 # bosh sahifa, mahsulot, profil, dashboard
│   │   ├── modules/               # cart, wishlist, qidiruv, auth oqimlari
│   │   ├── builder/               # CMS bo'lim render (hero, banner, slider...)
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
│   ├── k8s/                       # kelajakda
│   └── ci/
├── docs/
│   ├── TZ_EN.md
│   ├── TZ_UZ.md (ushbu hujjat)
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DB_SCHEMA.md
│   └── CHANGELOG.md
└── scripts/
```

Har bir Django ilovasida MAJBURIY:
`models.py · serializers.py · views.py · urls.py · services.py · selectors.py · tasks.py · admin.py · permissions.py · tests/`

- **services.py** — biznes mantiq (yozish, side-effect, tranzaksiya)
- **selectors.py** — o'qish so'rovlari (mutatsiyasiz, optimallashtirilgan queryset)
- **tasks.py** — Celery async vazifalar

---

## 6. ROLLAR VA RUXSATLAR

### 6.1 Rollar ierarxiyasi

| Rol | Tavsif | Ommaviy profil | Sotuv | Xarid | Admin panel |
|-----|--------|----------------|-------|-------|-------------|
| `customer` | Oddiy mijoz, jismoniy yoki yuridik | ❌ | ❌ | ✅ | ❌ |
| `seller` | Tashqi sotuvchi / ishlab chiqaruvchi / mutaxassis | ✅ | ✅ | ✅ | Cheklangan (o'z ma'lumoti) |
| `internal_supplier` | Bittada o'z ta'minotchi akkauntlari | ✅ | ✅ | ✅ | Cheklangan |
| `admin` | Bittada xodimi (moderatsiya, support, kontent) | ❌ | ❌ | ❌ | ✅ qisman |
| `super_admin` | Platforma egasi | ❌ | ❌ | ❌ | ✅ to'liq |

### 6.2 Akkaunt turi (rolga ortogonal)

- `individual` — jismoniy shaxs, oddiy KYC
- `company` — yuridik shaxs, ro'yxatdan o'tish hujjatlari, muhr/sertifikatlar

### 6.3 Sotuvchining sub-kategoriyalari (kasbiy parent)

Sotuvchi ro'yxatdan o'tishda bir yoki bir nechta kasbni tanlaydi:

- `supplier` (yetkazib beruvchi)
- `manufacturer` (ishlab chiqaruvchi)
- `master` (usta — qo'l ustasi, o'rnatuvchi, ta'mirchi)
- `designer` (interyer, mahsulot, grafik)

Har bir sub-kategoriya qo'shimcha profil maydonlarini ochadi (portfolio, sertifikatlar, ish vaqti).

### 6.4 Ruxsat matritsasi

- Har bir rol uchun standart ruxsatlar oldindan o'rnatiladi.
- Super Admin rol va aniq foydalanuvchi uchun ruxsatlarni o'zgartirishi/qo'shishi mumkin.
- Granularity: object-level ("faqat o'z mahsulotini tahrirlash"), action-level (CRUD), va field-level ("tannarx ko'rsatilmasin").
- Django Guardian yoki maxsus permission jadvali orqali (qaror `ARCHITECTURE.md` da yoziladi).

### 6.5 Profil ko'rinishi qoidalari

- `customer` → ommaviy sahifa yo'q, `/u/{username}/` URL mavjud emas.
- `seller` / `internal_supplier` → standart bo'yicha ommaviy sahifa yoqilgan; foydalanuvchi public/private deb almashtirishi mumkin.
- Yopiq profil → faqat oldin chat tarixi bo'lgan tizimga kirgan foydalanuvchilar ko'radi.

---

## 7. FOYDALANUVCHI PROFILI SPETSIFIKATSIYASI

### Foydalanuvchi tahrirlay oladigan:
- account_type (individual / company)
- ism, familiya (yoki kompaniya nomi)
- username (noyob, slug, URL da: `/u/{username}`)
- avatar — 6 tagacha rasmli galereya, biri asosiy
- cover (muqova) rasmi
- bio (rich text, ko'p tilli UZ/RU/EN)
- telefonlar (ro'yxat, har birining ko'rinish flagi: ochiq / pullik ochiladigan / yopiq)
- email (xuddi shu flaglar)
- telegram username
- veb-sayt
- manzil (matn + geo koordinatalar)
- ish vaqti (haftaning har kuni)
- hujjatlar (KYC) — yuklangan, admin tasdiqlaydi
- kasbiy parent (yetkazib beruvchi / ishlab chiqaruvchi / usta / dizayner — multi-select)

### Tizim boshqaradigan:
- reyting (0.0 – 5.0, izohlardan hisoblanadi)
- review_count
- tasdiqlangan holati (admin)
- joined_at
- last_seen
- profile_views (umrlik)
- tashrifchilar jurnali (admin/sotuvchi kim qachon kirganini ko'radi)

### Maxfiylik nazorati:
- Telefon, email, manzil ko'rinishi (ochiq / pullik / yopiq)
- Aniq foydalanuvchini bloklash
- Ommaviy sahifa umumiy o'chirgich (sotuvchilar uchun)

---

## 8. AUTENTIFIKATSIYA VA RO'YXATDAN O'TISH

### 8.1 Usullar (admin yoqib/o'chirib turadi)

1. Google OAuth2
2. Email + parol + OTP tasdiq
3. Telefon + SMS OTP
4. Telegram Login Widget

Har bir usul Super Admin paneldan kodga teginmasdan yoqib/o'chiriladi.

### 8.2 Xavfsizlik

- **Rate limit:** 5 noto'g'ri urinish → vaqtinchalik blok (15 min) → IP blokga eskalatsiya.
- **Qurilma kuzatuvi:** har bir kirish IP, user-agent, geo-IP yozadi; foydalanuvchi sessiyalarni ko'rib/bekor qilishi mumkin.
- **JWT rotation:** access (15 min) + refresh (14 kun, har ishlatishda yangilanadi + blacklist).
- **Parol siyosati:** kamida 10 belgi, 1 raqam, 1 belgi; bcrypt/argon2 hash.
- **2FA ixtiyoriy:** sotuvchi va admin uchun TOTP (admin/super_admin uchun majburiy).

### 8.3 Audit jurnali

Har bir auth hodisasi (login, logout, parol o'zgarishi, rol o'zgarishi, OAuth bog'lash) `security.audit_log` ga to'liq kontekst bilan yoziladi (kim, kimga, ip, ua, oldin/keyin).

---

## 9. DINAMIK CMS SAHIFA QURUVCHI

### 9.1 Imkoniyat

Adminlar maxsus URL slug bilan CHEKSIZ statik/CMS sahifa yarata oladilar. Misollar:
- `/about`
- `/contact`
- `/services`
- `/furniture`
- `/manufacturers/tashkent`

### 9.2 Sahifa maydonlari

- `title` (ko'p tilli)
- `slug` / to'liq URL (validatsiyalangan, noyob, parent_page orqali ierarxik)
- `parent_page` (null bo'lishi mumkin) → ichma-ich URL (`/services/installation`)
- `permission` (ochiq / autentifikatsiyalangan / rolga cheklangan)
- `visibility` (qoralama / rejalashtirilgan / nashr qilingan / arxiv)
- `seo_title`, `seo_description`, `seo_keywords`, `og_image`, `canonical_url`, `noindex` flag
- `template` (default / landing / docs / form)
- `header_variant`, `footer_variant`
- `custom_css`, `custom_js` (sandbox, faqat super_admin)

### 9.3 Bo'lim turlari (drag-drop)

- Hero blok (rasm/video fon, sarlavha, CTA)
- Banner
- Oddiy matn
- Rich text (TipTap / ProseMirror uslubidagi muharrir)
- Mahsulot slider (kategoriya/teg bo'yicha filter)
- Xizmat slider
- Kategoriya gridi
- FAQ akkordeon
- Rasm galereyasi
- Video embed
- 3D model embed (GLB)
- Maxsus HTML / CSS / JS blok (sandboxed iframe)
- CTA tugmasi
- Mijoz fikrlari (testimonials)
- Forma (lead-capture, CRM ga ulanadi)

### 9.4 Bo'lim ruxsatlari

Har bir bo'limning o'z ko'rinishi: ochiq / rolga cheklangan / yashirin. Masalan, "ulgurji narxlar" bo'limi faqat tasdiqlangan sotuvchilarga ko'rinishi mumkin.

### 9.5 Versiya nazorati

- Sahifaning har bir tahriri revisiya yaratadi (avtosaqlash).
- Admin istalgan revisiyaga qaytishi mumkin.

---

## 10. MAHSULOT MODULI

### 10.1 Mahsulot turlari

1. `standard` — jismoniy mahsulot, dona-dona sotiladi, `/shop` da chiqadi
2. `manufacturing` — buyurtma asosida, MOQ + MAX cheklovi, narx oralig'i
3. `service` — `/services` da chiqadi, vaqt yoki ish hajmi bo'yicha (alohida UI)

### 10.2 Umumiy maydonlar

- `title` (ko'p tilli UZ/RU/EN, AI orqali matn yaratish yordami)
- `description` (rich text, ko'p tilli)
- `category` (daraxt shaklidagi FK)
- `subcategory_path` (tezroq filter uchun denormalizatsiya)
- `sku` (avtomatik yoki qo'lda)
- `uuid` (o'zgarmas ommaviy id)
- `hashtags` (erkin matn, vergul bilan, qidiruv uchun indeksli)
- `tags` (saralangan teglar, FK)
- `price` (joriy)
- `old_price` (chizilgan)
- `min_price` / `max_price` (faqat manufacturing — oraliq)
- `discount_percent`, `discount_start`, `discount_end`, `discount_quantity` (miqdor bo'yicha qo'shimcha)
- `stock_qty` (standart) — warehouse modulidan olinadi
- `moq` minimal buyurtma (manufacturing)
- `max_qty` bitta buyurtmadagi maksimum
- `variants`: rang, o'lcham, material — ochiq atribut sxemasi
- `images` (10 ta gacha, tartibli, har til uchun alt matn)
- `video` (ixtiyoriy)
- `glb_models` (bir nechta — asosiy + variantlar masalan rang bo'yicha)
- `downloadable_files` (ochiq — har kim yuklab oladi)
- `production_files` (yopiq — so'rov-ruxsat oqimi)
- `blueprint_files` (yopiq — so'rov-ruxsat oqimi)
- `visibility_rules` har bir fayl/guruh uchun (ochiq / so'rov bilan / pullik)

### 10.3 Yopiq faylga kirish oqimi

Foydalanuvchi yopiq faylga so'rov yuborganda:
1. Egasi xabar oladi (in-app, email, telegram).
2. Xabarda so'rovchining profili, IP, qurilma, lokatsiya, xabari bo'ladi.
3. Egasi: ruxsat berish / rad etish / pulli ruxsat (narx belgilash) ni tanlaydi.
4. Hammasi audit jurnaliga yoziladi.

### 10.4 Chegirmalar

- Foiz yoki belgilangan summa
- Vaqt cheklovi (boshlanish/oxir)
- Miqdor bo'yicha qo'shimcha chegirma (masalan, qty ≥ 50 da +5%)
- Stack qoidalari aniq ustunlik bilan (admin belgilaydi)

### 10.5 Mahsulot analitikasi (har biri uchun)

- Umumiy ko'rishlar (noyob + jami)
- Tashrifchilar ro'yxati (kim, qachon, qayerdan) — egasi ko'radi
- Savatga qo'shilgan soni
- Wishlist soni
- Aloqa bosish soni
- Buyurtmaga konversiya
- Kunlik / haftalik / oylik grafik
- Manba (organic, internal search, reklama, referral)

---

## 11. XIZMATLAR MODULI

Xizmatlar UI mahsulotdan keskin farq qiladi:

- Booking uslubidagi listing
- Ta'minotchining bo'sh vaqt kalendari
- Mijoz ko'radigan status taymlayni (navbatda / rejalashtirilgan / jarayonda / yakunlangan / bekor qilingan)
- Jonli progress oqimi: ta'minotchi yangilanish, rasm, "hozir manzilda: X" yozishi mumkin
- Ochiq vs yopiq holat ommaga ko'rinadi (mijoz qaysi xizmat hozir band, qaysi yangi olishi mumkinligini ko'radi)
- To'lov escrow orqali

---

## 12. KATEGORIYA TIZIMI

- Cheksiz daraxt (Materialized Path yoki MPTT)
- Faqat admin / super_admin yarata/o'zgartira oladi
- Maydonlar:
  - nom (ko'p tilli)
  - ikonka (svg/png)
  - cover rasm
  - SEO meta (title, description, og_image)
  - ko'rinish / status
  - mahsulot turi filtri (standart / ishlab chiqarish / xizmat / aralash)
  - ruxsat (ochiq / rolga cheklangan)
- Har bir kategoriya sahifasining o'z SEO va ixtiyoriy CMS bo'limlari (kategoriya uchun mini lending sahifa).

---

## 13. CHAT TIZIMI

- Real-time, Django Channels (WebSocket).
- Cheklangan tarmoqlar uchun long-poll fallback.
- Xabar turlari:
  - matn
  - emoji
  - rasm (thumbnail bilan)
  - fayl (har qanday tur, virusga skanerlangan)
  - video
  - ovozli xabar (browser MediaRecorder)
  - lokatsiya (geo + xarita ko'rinishi)
  - quote (mahsulot/buyurtmaga link)
- O'qildi belgisi, terish indikatori, online/last-seen.
- Buyurtmaga bog'langan chat: so'rov/buyurtma bo'lsa, thread shu bilan bog'lanadi.
- Moderatsiya: admin shikoyat qilingan threadni o'qishi/muzlatishi mumkin (audit bilan).
- Media — diskda shifrlangan; olish uchun signed URL.

---

## 14. BUYURTMA TIZIMI (KO'P BOSQICHLI)

| # | Bosqich | Izoh |
|---|---------|------|
| 1 | So'rov (Inquiry) | Mijoz savol beradi, majburiyat yo'q |
| 2 | Taklif (Offer) | Sotuvchi rasmiy taklif (narx, shart, muddat) |
| 3 | Muzokara | Qarama-qarshi takliflar, chat orqali |
| 4 | Escrow to'lov | Mablag' Bittada hamyonida saqlanadi |
| 5 | Boshlangan | Ishlab chiqarish/yetkazish boshlandi |
| 6 | Ishlab chiqarish | (faqat manufacturing) bosqichlar, rasm, ETA |
| 7 | Yetkazish | Kuryer integratsiyasi, kuzatuv raqami |
| 8 | Yetkazib berildi | Mijoz tasdiqlaydi |
| 9 | Yakunlangan | Escrow sotuvchiga o'tkaziladi |
| 10 | Sharhlangan | Mijoz reyting/izoh qoldiradi |

- Nizolar 4-bosqichdan boshlab istalgan vaqtda ochiladi.
- Har bir o'tish kim, qachon, sabab bilan loglanadi.
- Sotuvchi kim savatga qo'shgan / so'rov yuborgan / buyurtma bergan ko'radi.

---

## 15. ESCROW VA HAMYON (Upwork uslubida)

- Har bir foydalanuvchining 2 ta ledgerli hamyoni bor:
  - `available_balance` — yechib olinadigan
  - `escrow_balance` — buyurtmalarda saqlangan
- Mijoz mablag' kiritadi → aniq buyurtma ostidagi `escrow_balance` ga o'tadi.
- Buyurtma yakunlanganda → sotuvchining `available_balance` ga o'tadi (komissiyani chegirib).
- Nizoda → admin arbitraji proportsional release/refund qiladi.
- Yechib olish so'rovlari → qo'lda yoki avto (bank shartiga qarab).
- Hamma tranzaksiya `escrow.transaction_log` ga o'zgarmas qator (double-entry) sifatida yoziladi.
- Sotuvchilar ham xaridor bo'la oladi va boshqa ta'minotchidan buyurtma bera oladi — bitta hamyon.

---

## 16. KREDIT / BALL IQTISODIYOTI

Kreditlar pullik harakatlarni boshqaradi:

| Harakat | Standart narx (sozlanadigan) |
|---------|-------------------------------|
| Sotuvchining telefonini ochish | 1 kredit |
| Sotuvchining emailini ochish | 1 kredit |
| Chatni boshlash | 2 kredit |
| Ustuvor lid kirish | 5 kredit |
| Listingni 24 soatga ustun qilish | 20 kredit |

- Kreditlar to'lov tizimi orqali sotib olinadi (Click, Payme, Uzcard, Visa, kripto-tayyor).
- Sotuvchi: kim aloqani ko'rgan, kim ochgan, qaysi biri buyurtmaga aylangan analitikasini ko'radi.
- "Aloqa ochish" sahifasi — alohida, ataylab UI qadami → tasodifiy hisob qoldirilmaydi.
- Har bir aloqa ochilishi loglanadi va sotuvchiga lid sifatida ko'rinadi.

---

## 17. OMBOR VA ZAXIRA

- Sotuvchi uchun ko'p ombor:
  - `home` (o'z uy / do'kon)
  - `external` (ijaraga olingan ombor)
  - `supplier` (yuqori ta'minotchidan drop-ship)
- SKU + ombor bo'yicha statuslar: `available`, `reserved`, `out_of_stock`, `incoming`.
- Buyurtmada rezervatsiya yaratiladi; bekor qilinganda bo'shatiladi.
- Yetkazish narxini hisoblash uchun har omborning geo koordinatasi.
- ERP sync (Odoo / 1C / MoySklad) zaxira solishtirib turadi.

---

## 18. ANALITIKA

### 18.1 Sotuvchi paneli
- Mahsulot ko'rishlari (har biri, har kun)
- Profil ko'rishlari (tashrifchilar ro'yxati)
- Manba (qidiruv / ijtimoiy / to'g'ridan-to'g'ri / referral)
- Savatga qo'shish, aloqa bosish, konversiya
- Buyurtma voronkasi (so'rov → yakun)
- Daromad grafigi (kun/hafta/oy/yil)
- Top mahsulotlar, sekin sotuvlar
- Lid sarfi (kreditlar) vs yutilgan buyurtmalar

### 18.2 Admin paneli
- GMV, take rate, faol sotuvchilar va mijozlar
- Cohort retention
- Top kategoriyalar va hududlar
- Firibgarlik signallari (multi-akkaunt, IP to'qnashuvi)

---

## 19. QORA RO'YXAT (Yopiq B2B Ishonch Moduli)

- Faqat rollar ko'radi: `seller`, `internal_supplier`, `admin`, `super_admin`.
- Mijozlar va omma KO'RA OLMAYDI.
- Yozuv turlari: `fraud_buyer`, `unpaid_buyer`, `scam_supplier`, `abuse`, `harassment`.
- Har bir yozuv: maqsad foydalanuvchi/tel/email, sabab, dalil (fayl/skrinshot), xabar bergan, sana, status (kutmoqda / tasdiqlangan / nizoli / tozalangan).
- Admin moderatsiya qiladi; sotuvchilar ishonchlilikka ovoz beradi; doimiy nizo yozuvni yashiradi.

---

## 20. 3D SHOWROOM (GLB Moduli)

- Har bir mahsulotga bir necha GLB model biriktiriladi (rang/variant bo'yicha).
- Har bir mahsulot uchun ommaviy iframe-embed sahifa: `/embed/glb/{product_uuid}/{variant_id}`.
- Kategoriya darajasidagi showroom: `/showroom/{category_slug}` faqat GLB ga ega mahsulotlarni ko'rsatadi.
- Embed kod yaratuvchi (copy-paste iframe HTML).
- Mobil AR ko'rinishi `<model-viewer>` web komponenti orqali.

---

## 21. SUPPORT MARKAZI

- **Tikets:** ochiq / jarayonda / hal qilingan / yopiq; muhimlik darajasi; SLA tayemer.
- **FAQ:** admin saralagan, ko'p tilli, qidiruvli.
- **Forum:** community Q&A, like ovoz, moderatsiya.
- **Shikoyatlar:** mahsulotga, foydalanuvchiga, kontentni o'chirish.
- **Rasm biriktirish** har bir tikets va shikoyatda.
- **Admin javob shablonlari** (canned).
- **Ichki eslatma** (faqat xodim ko'radi).

---

## 22. SEO

Har bir obyekt (sahifa, mahsulot, profil, kategoriya) uchun:
- `meta_title`, `meta_description`, `keywords`
- Open Graph teglar (`og:title`, `og:description`, `og:image`, `og:type`)
- Twitter card
- `canonical` URL
- JSON-LD schema (Product, Service, Organization, BreadcrumbList, Review, FAQPage)
- Avtomatik `sitemap.xml` (obyekt turi bo'yicha bo'lingan, sahifalangan)
- `robots.txt` admin tahrir qilinadi
- Slug qoidalari: kichik harf, defis, ko'p tilli transliteratsiya xavfsiz
- 301 redirektlar (admin boshqaradigan jadval)
- v1 da AMP shart emas.

---

## 23. KO'P TILLILIK

- Standart tillar: **O'zbek (uz)**, **Rus (ru)**, **Ingliz (en)**.
- Super Admin dinamik ravishda yangi til qo'sha oladi (DB asosida, kodga teginmasdan).
- Hamma user-facing matn tarjima qator sifatida saqlanadi; UI Django i18n (`gettext`) statik uchun + tarjima jadvali dinamik uchun.
- Mahsulot yaratish formi 3 ta standart tilni talab qiladi (sozlanadigan: majburiy/ixtiyoriy).
- AI matn yordami: foydalanuvchi qoralama yozadi, AI mukammal tarjimada qaytaradi (OpenAI/Claude API, provayder sozlanadi).
- Header da til tanlash; user uchun saqlanadi, mehmon uchun cookie.

---

## 24. ERP / CRM INTEGRATSIYALARI

Tayyor konnektorlar (admin har bir sotuvchi uchun yoqadi):
- **Odoo** (REST + XML-RPC)
- **Bitrix24** (REST)
- **1C** (fayl almashinuvi + REST adapter)
- **MoySklad** (REST)
- **Didox** (e-faktura / EDI O'zbekiston)
- **Custom** webhook + REST shablon

Sinxronlash maqsadlari:
- Zaxira (ikki tomonlama)
- Buyurtmalar (Bittada → ERP)
- Mijozlar (Bittada → CRM)
- Hisob-fakturalar (ERP → Bittada ko'rinish uchun)
- Mahsulot katalogi (ERP → Bittada yoki teskari, integratsiya sozlamasiga qarab)

---

## 25. OCHIQ API

- Versionlangan: `/api/v1/...`
- Auth: JWT bearer yoki API token (har integratsiya uchun).
- Token bo'yicha rate limit (sozlanadigan tariflar).
- OpenAPI 3 spetsifikatsiyasi avto-yaratiladi, `/api/docs` da.
- Webhook: obuna bo'lsa bo'ladigan hodisalar (order.created, order.completed, stock.changed, message.received), HMAC imzolangan.
- Maqsad: mobil ilovalar (iOS / Android), hamkor ERP, kuryer integratsiyalari, tashqi do'konlar.

---

## 26. XAVFSIZLIK (MAJBURIY)

| Nazorat | Talab |
|---------|-------|
| CSRF | Sessiya viewlarida Django CSRF middleware |
| XSS | Auto-escape; CSP qattiq; rich text save da sanitize |
| SQLi | Faqat ORM; foydalanuvchi inputi bilan raw SQL yo'q; agar kerak bo'lsa parameterized |
| Rate limit | DRF throttling + Redis hisoblagich; per-IP + per-user |
| IP blok | Qo'lda + avto (failed login, suiiste'mol) |
| Brute-force | 5 fail → 15 min blok → IP blokga eskalatsiya |
| Qurilma kuzatuvi | Sessiya yozuvi + bekor qilish |
| Audit jurnali | Admin harakatlari, rol o'zgarishi, moliyaviy hodisalar |
| Ruxsat matritsasi | Object-level + field-level |
| Headerlar | HSTS, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy strict-origin-when-cross-origin, minimal Permissions-Policy |
| Fayl validatsiyasi | MIME sniff + extension whitelist; rasmlarni qayta-encode; non-image uchun ClamAV |
| JWT | Qisqa access + rotating refresh + logoutda blacklist |
| Sessiya | Ro'yxat + bekor qilish; nozik amallarda qayta auth |
| Sirlar | Faqat `.env`, git da yo'q; vault-tayyor |
| Disk shifrlash | Media bucket shifrlangan; KYC PII column-level shifrlash |
| GDPR uslubi | Akkauntni o'chirish + ma'lumot eksport endpointi |

---

## 27. UI / UX STANDARTLARI

### Uslub
- Minimalistik, premium, korporativ
- Yetarli bo'sh joy
- Mobile-first responsive
- Yumshoq, maqsadli animatsiyalar (≤ 200ms, jankisiz)

### Header (sticky)
- Logo
- Mega menu (kategoriyalar)
- Universal qidiruv (mahsulot, xizmat, sotuvchi, hashtag)
- Til almashtirgich
- Login / register
- Sevimlilar
- Savat
- Bildirishnoma qo'ng'irog'i
- Dashboard kirish (rolga qarab)

### Footer (dinamik)
- Biz haqimizda
- Aloqa
- Siyosatlar (shart, maxfiylik, qaytarish)
- Yordam markazi
- Ijtimoiy linklar
- Ilova yuklab olish
- Newsletter
- Til almashtirgich

Header va Footer CMS orqali tahrir qilinadi (bo'limlar, linklar, bannerlar) — sahifalar bilan bir xil builder.

---

## 28. DEPLOY VA KELAJAKDAGI AJRATISH

### v1 (yagona host)
- Docker Compose: nginx, backend (gunicorn), channels (daphne), postgres, redis, celery worker, celery beat, minio.

### v2 (kodga teginmasdan ajratiladigan)
- frontend server (statik + edge cache)
- backend server (REST API)
- websocket server (Channels)
- media server (S3 / MinIO)
- search server (Meilisearch)
- worker pool (Celery)

Servislar orasidagi trafik signed JWT orqali; umumiy fayl tizimi yo'q.

---

## 29. KOD SIFATI QOIDALARI

- Hamma joyda type hint (Python 3.12 typing).
- Lint: kritik ilovalarda `ruff` + `black` + `mypy --strict`.
- Test: `pytest` + coverage gate (services + selectors da ≥ 80%).
- Komentariya faqat NIMA UCHUN aniq bo'lmagan joyda. NIMA QILYAPTI ni takrorlamaslik.
- Conventional commits.
- PR checklist: testlar, migratsiya xavfsizligi, doc, security review.

---

## 30. YO'L XARITASI (BOSQICHMA-BOSQICH)

| Bosqich | Qamrov | Natija |
|---------|--------|--------|
| **P0 — Asos** | Repo skelet, settings, auth, users, RBAC, admin, CI, base UI shell | Login bo'ladigan platforma, header/footer, bo'sh sahifalar |
| **P1 — Katalog yadrosi** | Kategoriyalar, mahsulot (standart), media quvuri, qidiruv, mahsulot/kategoriya sahifasi | Ko'rib chiqiladigan katalog |
| **P2 — Profil va Chat** | Sotuvchi ommaviy profili, chat (WebSocket), profil tahrirlash | Mijoz-sotuvchi muloqoti |
| **P3 — Buyurtma va Escrow** | Savat, checkout, buyurtma sikli, escrow hamyon, to'lovlar | Birinchi to'liq tranzaksiya |
| **P4 — Manufacturing va Xizmat** | MOQ/oraliq mahsulot, xizmatlar moduli, booking taymlayni | Buyurtma asosida B2B jonli |
| **P5 — CMS Builder** | Dinamik sahifa, bo'lim, header/footer builder, SEO | Kontent jamoasi mustaqil |
| **P6 — 3D va Fayllar** | GLB embed, chizma so'rov oqimi, showroom sahifalari | 3D-asosli savdo |
| **P7 — Kreditlar va Analitika** | Kredit iqtisodi, aloqa ochish, sotuvchi va admin analitikasi | Monetize qilingan lidlar |
| **P8 — Integratsiyalar** | Odoo, Bitrix24, 1C, MoySklad, Didox, ochiq API, webhook | ERP-darajadagi sotuvchilar |
| **P9 — Ko'p tillilik va AI matn** | UZ/RU/EN majburiy, AI yordamchi, til admin | Xalqaro tayyor |
| **P10 — Mustahkamlash** | Security audit, load test, SEO audit, accessibility audit, ishga tushirish | GA |

---

## 31. QABUL MEZONLARI (har bosqichda, qisqa)

- Hamma endpoint OpenAPI da hujjatlangan.
- Hamma ilovada `services.py` + `selectors.py` + testlar.
- Yuk testida p95 latensiya budjet (1000 RPS).
- OWASP ZAP skan: high/critical 0.
- Lighthouse: top 10 sahifada Performance ≥ 90, Accessibility ≥ 95, SEO ≥ 95.
- Admin sozlay oladigan hamma narsa kodga teginmasdan sozlanadi.
- CI yashil; staging prod sxemasiga mos.

---

## 32. v1 GA KIRMAYDIGAN

- Native mobil ilovalar (faqat API tayyor).
- Kripto to'lovlar (faqat hooklar).
- Jonli video stream.
- Auksion.
- Obuna mahsulotlari (qayta-qayta to'lov).
- Reklama / sponsorlik (kredit-boost dan tashqari).

---

## 33. SO'ZLIK

- **MOQ** — Minimal Buyurtma Miqdori.
- **GMV** — Umumiy Tovar Aylanmasi.
- **Escrow** — Shartlar bajarilmaguncha platformada saqlanadigan mablag'.
- **GLB** — Binary glTF, 3D model formati.
- **ERP** — Korxona resurslarini boshqarish.
- **CMS** — Kontent boshqaruv tizimi.
- **KYC** — Mijozni biling (shaxsni tasdiqlash).

---

## 34. TASDIQ

Bu hujjat tasdiqlanishi kerak:
- [ ] Asoschi / Mahsulot egasi
- [ ] Texnik rahbar
- [ ] Xavfsizlik rahbari
- [ ] UX rahbari

Tasdiqlangandan so'ng ish §30 dagi tartibda boshlanadi. Har qanday o'zgartirish `docs/CHANGELOG.md` da yoziladi va Texnik rahbar tomonidan ko'rib chiqiladi.

---

**HUJJAT OXIRI — TZ_UZ.md v1.0**
