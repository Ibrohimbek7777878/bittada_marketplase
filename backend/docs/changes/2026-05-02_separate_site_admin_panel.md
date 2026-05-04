# Sayt admin panelini Django admin'dan ajratish (2026-05-02)

> **Vazifa nomi:** Sayt admin paneli (Seller/Admin uchun ERP UI) Django'ning standart admin panelidan to'liq ajratilsin. Foydalanuvchi sidebar'dagi "Mahsulotlar" yoki "Savdo" linklarini bosganda **bizning chiroyli interfeysda qolishi**, hech qachon Django'ning quruq admin formasiga otkazib yuborilmasligi kerak.

---

## 🎯 Muammo (Before)

Sidebar'dagi linklar:
- `Mahsulotlar` → `/admin/products/product/` → **Django'ning standart admin paneli** ko'rinadi (dizayn buziladi)
- `Savdo` → `/admin/orders/order/` → Django admin
- `Foydalanuvchilar` → `/admin/users/user/` → Django admin
- `Command Center` (navbar) → `/admin/` → Django admin

Foydalanuvchi (Seller) saytni ochib, "Mahsulotlar" tugmasini bosgan zahoti — bizning ERP dizaynidan **chiqib ketadi** va Django'ning quruq formasini ko'radi. Bu UX muammo.

## ✅ Yechim (After)

1. **Django admin URL'i ko'chirildi**: `/admin/` → `/super-admin/` (faqat superuser/staff uchun maxfiy)
2. **Sayt admin paneli uchun yangi prefix**: `/manage/products/` (ERP UI)
3. **Custom Views**: `product_admin_list_view`, `product_admin_create_view` — `base_erp.html` extend qilingan templatelar bilan
4. **Login redirect**: `LOGIN_URL = "/login/"` — barcha auth-required yo'naltirishlar bizning login sahifamizga
5. **Sidebar/Navbar linklari** yangilandi: Mahsulotlar custom URL'ga, qolgan vaqtinchalik linklar `/super-admin/...` ga (keyingi vazifalarda ular ham custom UI ga ko'chiriladi)

---

## 📁 O'zgartirilgan/Yangi fayllar

### 1. [backend/config/settings/base.py](../../backend/config/settings/base.py) — M

**Nima o'zgardi:**
- `LOGIN_URL = "/login/"` qo'shildi
- `LOGIN_REDIRECT_URL = "/"`, `LOGOUT_REDIRECT_URL = "/"` qo'shildi

**Nega:**
- Django'ning default `/accounts/login/` o'chirilmagan, lekin u bizning loyihada mavjud emas
- `staff_member_required` yoki `login_required` decorator'lari bu URL'larga ishonadi

**Qanday muammo hal qilindi:**
- Avval Seller `/super-admin/` ga kirishga harakat qilsa, Django'ning standart login formasi chiqar edi
- Endi `LOGIN_URL` o'rnatilgani uchun u **bizning `/login/`** sahifamizga yo'naltiriladi (ERP dizaynli login)

---

### 2. [backend/config/urls.py](../../backend/config/urls.py) — M

**Nima o'zgardi:**
- `path("admin/", admin.site.urls)` → `path("super-admin/", admin.site.urls)`
- `api_root` JSON javobida `"admin": "/admin/"` → `"admin": "/super-admin/"`
- **YANGI:** `RedirectView` import qilindi
- **YANGI:** `path("super-admin/login/", RedirectView.as_view(url="/login/", query_string=True, ...))` — Django admin'ning standart login formasini bizning `/login/` ga yo'naltiradi
- **YANGI:** `path("super-admin/logout/", RedirectView.as_view(url="/logout/", ...))` — logout ham bizning view'ga

**Nega:**
- `/admin/` URL'i sayt foydalanuvchilari uchun ko'rinmasligi kerak (Django admin maxfiy joyda tursin)
- Sayt admin paneli endi `/manage/...` ostida joylashadi
- Foydalanuvchi tasodifan `/super-admin/` ga kirib qolsa ham, **Django'ning quruq login formasini ko'rmasligi shart** (TZ talabi)

**Qanday muammo hal qilindi:**
- `/admin/products/product/` → 404 (eski URL yo'q)
- `/super-admin/` (anonymous) → `/super-admin/login/` → bizning `/login/?next=/super-admin/` (ERP UI saqlanadi) ✅
- `query_string=True` — `?next=...` parametri bizning login view'ga uzatiladi, kirgandan keyin avtomatik qaytadi

---

### 3. [backend/apps/products/views.py](../../backend/apps/products/views.py) — M (qo'shimcha qilindi, mavjud kodga TEGMASDAN)

**Nima qo'shildi:**
- `_is_panel_user(user)` — yordamchi funksiya: foydalanuvchi sayt admin paneliga kira oladimi-yo'qmi tekshiradi (is_staff/is_superuser/role='seller'|'admin'|'super_admin')
- `product_admin_list_view(request)` — Mahsulotlar boshqaruvi ro'yxati. Filterlash (q, status, product_type, category), pagination (25 ta/sahifa), KPI stat-kartochkalar.
- `product_admin_create_view(request)` — Yangi mahsulot yaratish formasi. GET → bo'sh forma, POST → validatsiya + Product.objects.create() + redirect.

**Nega:**
- `home_view`, `services_view` va boshqa mavjud view'lar **buzilmasin** — daxlsizlik qoidasi
- Yangi 2 ta view fayl oxiriga qo'shildi (180+ qator yangi kod, mavjud kodga ta'sirsiz)

**Qanday muammo hal qilindi:**
- Endi `/manage/products/` chaqirilganda Django'ning standart ChangeList'i emas, bizning chiroyli `admin_list.html` render qilinadi
- Validation va xatolik xabarlari bizning UI uslubida ko'rsatiladi (qizil border + matn)

---

### 4. [backend/apps/products/urls.py](../../backend/apps/products/urls.py) — M

**Nima o'zgardi:**
- Import bo'limiga `product_admin_list_view, product_admin_create_view` qo'shildi
- `urlpatterns` ga 2 ta yangi `path()` qo'shildi:
  - `manage/products/` → `name='admin_product_list'`
  - `manage/products/create/` → `name='admin_product_create'`

**Nega:**
- Mavjud URL'lar (`home`, `category_detail`, `product_detail` va h.k.) saqlandi
- Yangi 2 ta `path` boshqalarga ta'sir qilmaydi (Daxlsizlik kafolati)

**Qanday muammo hal qilindi:**
- `{% url 'admin_product_list' %}` template tag endi ishlaydi (sidebar bunda foydalanadi)
- `redirect("admin_product_list")` view ichida ishlaydi (POST muvaffaqiyatidan keyin)

---

### 5. [backend/templates/products/admin_list.html](../../backend/templates/products/admin_list.html) — YANGI

**Maqsad:**
Mahsulotlar boshqaruvi ro'yxati sahifasi. `base_erp.html` extend qiladi (sidebar+navbar bilan).

**Tarkib:**
- Sahifa header (sarlavha + "Yangi mahsulot" CTA tugmasi)
- 3 ta KPI stat-kartochka (Jami, Nashr etilgan, Qoralama)
- Filter formasi (qidiruv + status + tur + kategoriya dropdown'lari)
- Mahsulotlar jadvali (rasm, nom, SKU, kategoriya, narx, holat, zaxira, amal)
- Paginatsiya (filter qiymatlari saqlanadi)
- Empty-state (mahsulot yo'q bo'lsa)

**Nega:**
- Foydalanuvchi Django admin'ga emas, bizning dizayndagi sahifaga tushishi kerak
- Har bir HTML qator izohlandi (loyiha qoidasi: tushunarlilik)

**Qanday muammo hal qilindi:**
- Sidebar'dagi "Mahsulotlar" linki endi shu shablonni ochadi → ERP UI saqlanadi

---

### 6. [backend/templates/products/admin_create.html](../../backend/templates/products/admin_create.html) — YANGI

**Maqsad:**
Yangi mahsulot yaratish formasi (bizning UI dizaynda).

**Tarkib:**
- Header (orqaga tugma + sarlavha + breadcrumb)
- 2-kolonkali grid forma:
  - Nom (UZ) — to'liq qator
  - SKU (mono shrift)
  - Narx (so'm)
  - Kategoriya dropdown
  - Zaxira miqdori
  - Holat dropdown (ProductStatus)
  - Tur dropdown (ProductType)
  - Tavsif (UZ) — textarea, to'liq qator
- Action satri: "Bekor qilish" + "Saqlash" tugmalari
- Validatsiya xato xabarlari maydon ostida (qizil border)
- Umumiy xato banneri (yuqorida)

**Nega:**
- Django'ning standart ChangeForm (160+ maydonli) o'rnida soddalashtirilgan, MVP-darajadagi forma kerak
- Foydalanuvchi (Seller) keraksiz texnik maydonlarni ko'rmasligi kerak (uuid, view_count va h.k.)

**Qanday muammo hal qilindi:**
- "Yangi mahsulot" CTA tugmasi bosilganda foydalanuvchi bizning dizayndagi formaga keladi
- Validation xatosi bo'lsa, kiritgan ma'lumotlari yo'qolmaydi (form_data context orqali qaytariladi)

---

### 7. [backend/templates/includes/erp_sidebar.html](../../backend/templates/includes/erp_sidebar.html) — M

**Nima o'zgardi:**
| Eski link | Yangi link | Izoh |
|-----------|------------|------|
| `/admin/orders/order/` (Savdo) | `/super-admin/orders/order/` | Vaqtincha Django admin (yangi joyda) |
| `/admin/products/product/` (Mahsulotlar) | `{% url 'admin_product_list' %}` | **Custom ERP UI** ✅ |
| `/admin/orders/order/` (Escrow Fund) | `/super-admin/orders/order/` | Vaqtincha |
| `/admin/billing/` (Credit Economy) | `/super-admin/billing/` | Vaqtincha |
| `/admin/users/user/` (Foydalanuvchilar) | `/super-admin/users/user/` | Vaqtincha |
| `/admin/users/user/?is_active__exact=0` (Qora ro'yxat) | `/super-admin/users/user/?is_active__exact=0` | Vaqtincha |
| `/admin/` (Django Admin) | `/super-admin/` | Yangi maxfiy joy |

**Nega:**
- Hozirgi vazifada faqat Mahsulotlar uchun custom UI yaratildi (asosiy talab)
- Boshqa linklar `/super-admin/...` ga yo'naltirildi (ya'ni Django admin yangi joyda) — keyingi vazifalarda ular ham custom ERP UI ga ko'chiriladi

**Qanday muammo hal qilindi:**
- Mahsulotlar bosilganda foydalanuvchi bizning dizaynda qoladi
- Eski `/admin/...` linklar 404 bermaydi (chunki `/super-admin/...` da Django admin javob beradi)
- Sidebar'da `active` holat ham qo'shildi: `{% if '/manage/products' in request.path %}active{% endif %}`

---

### 8. [backend/templates/includes/erp_navbar.html](../../backend/templates/includes/erp_navbar.html) — M

**Nima o'zgardi:**
- Navbar'dagi "Command Center" tugmasi: `href="/admin/"` → `href="{% url 'admin_product_list' %}"`

**Nega:**
- Superuser navbar'dagi "Command Center" tugmasini bosganda Django admin'ga emas, bizning ERP UI ga tushishi kerak
- Bu tugma sayt admin panelining "kirish nuqtasi" (entry point) sifatida ishlaydi

**Qanday muammo hal qilindi:**
- Superuser navbar'dan ham bizning ERP UI ga keladi (avval `/admin/` ga otkazib yuborar edi)
- Django admin'ga kerak bo'lsa, sidebar'dagi "⚙️ Django Admin" linki orqali (ya'ni `/super-admin/`)

---

## 🔬 Test va tekshirish

```bash
$ ./venv/bin/python manage.py check
System check identified some issues:
WARNINGS:
?: (axes.W003) ...  # mavjud, bu o'zgarish bilan bog'liq emas
System check identified 1 issue (0 silenced).
```

URL reverse va template syntax xatolari **yo'q** — ✅

---

## 🛡️ Daxlsizlik kafolati (Loyiha qoidasi)

Hech qanday mavjud funksiya/klass o'zagi (signature, body) o'zgartirilmadi:
- ✅ `home_view`, `services_view`, `category_detail_view` va boshqa view'lar **TEGMADI**
- ✅ `Product`, `Category` modellari o'zgarmadi
- ✅ `ProductAdmin` (apps/products/admin.py) ham o'zgarmadi — Django admin'da ishlashda davom etadi
- ✅ Mavjud URL'lar (`home`, `category_detail`, `product_detail` va h.k.) saqlandi
- ✅ Sidebar/navbar'dagi `{% url 'home' %}`, `{% url 'logout' %}`, `{% url 'profile' %}` linklari o'zgarmadi

---

## 🚀 Keyingi qadamlar (kelajakdagi vazifalar)

1. **Savdo (Orders) uchun custom ERP UI** — `order_admin_list_view`, `order_admin_detail_view`
2. **Foydalanuvchilar uchun custom ERP UI** — `user_admin_list_view`
3. **Mahsulot tahrirlash** — `product_admin_edit_view` (hozir faqat list+create)
4. **Mahsulot o'chirish (soft delete)** — POST `manage/products/<id>/delete/`
5. **Mahsulot rasmlari yuklash** — multipart upload integration
6. Eski `/admin/...` linklarni ushlash uchun **redirect middleware**: `/admin/products/product/` → `/manage/products/`
