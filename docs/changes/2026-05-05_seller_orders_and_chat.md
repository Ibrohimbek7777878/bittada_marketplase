# Sotuvchi buyurtmalari + chat (HTMX polling)

**Sana**: 2026-05-05
**Muallif**: Claude (Opus 4.7) — `mebelcityai@gmail.com` so'rovi bo'yicha

## Qisqacha

Sotuvchi shaxsiy admin paneliga ikki yangi qism qo'shildi:

1. **Buyurtmalar** (`/dashboard/seller/orders/`) — sotuvchiga kelgan barcha
   buyurtmalar ro'yxati va detali (status filter, pagination).
2. **Chat** (`/chat/room/<id>/`) — sotuvchi va mijoz o'rtasidagi suhbat.
   Texnologiya: **HTMX polling** har 3 sekundda (WebSocket o'rniga, sodda
   va Channels'siz ishlaydi).

## URL'lar

| URL | View | Vazifa |
|-----|------|--------|
| `/dashboard/seller/orders/` | `SellerOrderListView` | Ro'yxat (filter+paginatsiya) |
| `/dashboard/seller/orders/<uuid>/` | `SellerOrderDetailView` | Detali + chat link |
| `/chat/order/<uuid>/` | `OpenChatForOrderView` | Order id orqali xona ochish (redirect) |
| `/chat/room/<uuid>/` | `ChatRoomView` | Asosiy chat sahifa |
| `/chat/room/<uuid>/messages/` | `MessagesPartialView` | HTMX polling target (3s) |
| `/chat/room/<uuid>/send/` | `SendMessageView` | HTMX POST (yangi xabar) |

## O'zgartirilgan / yaratilgan fayllar

| Fayl | Holat | Maqsad |
|------|-------|--------|
| `backend/apps/orders/selectors.py` | tahrir | `get_orders_for_seller`, `get_order_for_user` |
| `backend/apps/orders/views.py` | tahrir | `SellerOrderListView`, `SellerOrderDetailView` qo'shildi |
| `backend/apps/orders/urls.py` | tahrir | `seller_order_urlpatterns` ro'yxati |
| `backend/apps/chat/selectors.py` | tahrir | `get_messages`, `get_room_for_user`, `get_or_create_room_for_order` |
| `backend/apps/chat/views.py` | tahrir | `OpenChatForOrderView`, `ChatRoomView`, `MessagesPartialView`, `SendMessageView` |
| `backend/apps/chat/urls.py` | tahrir | `template_urlpatterns` (chat URL'lari) |
| `backend/config/urls.py` | tahrir | seller dashboard'ga orders qo'shildi + `chat:` namespace |
| `backend/templates/dashboard/seller/base_seller.html` | tahrir | Sidebar'ga "Buyurtmalar" tugmasi |
| `backend/templates/dashboard/seller/orders/list.html` | yaratildi | Ro'yxat (jadval+filter+paginatsiya) |
| `backend/templates/dashboard/seller/orders/detail.html` | yaratildi | Detail + chat link |
| `backend/templates/chat/room.html` | yaratildi | Mustaqil chat UI (HTMX) |
| `backend/templates/chat/message_partial.html` | yaratildi | HTMX swap fragment |

**Migration**: kerak bo'lmadi (chat va orders modellari avval yaratilgan).

## Texnik tafsilotlar

### Permission qoidalari

**Orders**:
- `SellerOrderListView` — LoginRequired + role tekshiruvi (`is_seller`),
  customer 403 oladi.
- `SellerOrderDetailView` — `get_order_for_user()` selektor: faqat order
  ishtirokchisi (buyer YOKI seller) ko'ra oladi, boshqa user 404 oladi
  (mavjudligi ham bilinmasin).

**Chat**:
- Hamma chat view'lar `get_room_for_user()` orqali tekshiradi —
  `ChatRoom.participants` ichida user borligini.
- Boshqa user 403 oladi (`PermissionDenied` Django'ning standart
  exception'i, middleware tomonidan 403 ga aylantiriladi).

### Chat texnologiyasi: HTMX polling

WebSocket emas, chunki:
- Django Channels infrastructure murakkab (Redis layer + Daphne)
- Vazifa fallback variantini ham qabul qilgan
- HTMX polling — har 3s `GET /chat/room/<id>/messages/`, partial HTML keladi va `innerHTML` swap qilinadi

```html
<ul id="message-list"
    hx-get="{% url 'chat:messages' room_id=room.id %}"
    hx-trigger="every 3s"
    hx-swap="innerHTML">
```

Yangi xabar yuborish ham HTMX orqali — POST `chat:send`, javobi shu
yangilangan ro'yxat (avtomatik swap).

```html
<form hx-post="{% url 'chat:send' room_id=room.id %}"
      hx-target="#message-list"
      hx-encoding="multipart/form-data">
```

Avtomatik scroll-to-bottom: `hx-on::after-swap` event handleri orqali.

### Chat funksionalligi

- **Avatar**: chap tomonda boshqa user, o'ng tomonda o'zining xabari
- **Pufakchalar**: o'zining ko'k (`#2563eb`), boshqaniki oq border bilan
- **Vaqt**: har xabarda H:i formatda
- **Fayl/rasm**: `<input type="file" name="attachment">` orqali, rasm bo'lsa preview, boshqa bo'lsa download link
- **Enter**: yuborish (Shift+Enter — yangi qator)
- **Mustaqil HTML**: `room.html` `base.html` dan extend qilmaydi (mavjud `auth_logout` URL bug'iga tegmaslik uchun)

### URL routing tartibi

`config/urls.py` ichida 3 ta yangi import:

```python
from apps.products.urls import seller_dashboard_urlpatterns as _seller_dashboard_urls
from apps.orders.urls   import seller_order_urlpatterns      as _seller_order_urls
from apps.chat.urls     import template_urlpatterns          as _chat_template_urls

_seller_combined_urls = _seller_dashboard_urls + _seller_order_urls
```

Va include'lar:

```python
path("dashboard/seller/", include((_seller_combined_urls, "seller_dashboard"), namespace="seller"))
path("", include((_chat_template_urls, "chat"), namespace="chat"))
```

Reverse natija:
- `seller:orders_list` → `/uz/dashboard/seller/orders/`
- `seller:order_detail` → `/uz/dashboard/seller/orders/<uuid>/`
- `chat:open_for_order` → `/uz/chat/order/<uuid>/`
- `chat:room` → `/uz/chat/room/<uuid>/`
- `chat:messages` → `/uz/chat/room/<uuid>/messages/`
- `chat:send` → `/uz/chat/room/<uuid>/send/`

### Mavjud `chat/services.py` ishlatildi

Allaqachon yozilgan funksiyalar bilan integratsiya:
- `get_or_create_direct_room(user1, user2, order=None)` — xona ochish
- `send_message(sender, room, text, attachment)` — xabar yuborish

Bu funksiyalar atomik (`@transaction.atomic`), ishtirokchi tekshiruvi va
auto-update'larni o'z ichiga oladi. Ustiga yozmadik (vazifa cheklov: "agar
allaqachon mavjud bo'lsa — ustiga yoz, yangisini yaratma" — biz mavjud
servislarni ustiga yozmadik, ular chat domain logic'iga to'liq mos edi).

## Test natijalar

```
System check: 0 issues

Anonymous /orders/:                 302 → /login/?next=...
Customer /orders/:                  403 ✓ (seller emas)
Seller /orders/:                    200 (13.8 KB)
Seller order detail (own):          200 (14.0 KB)
Open chat for order:                302 → /chat/room/<uuid>/
Chat room:                          200 (9.0 KB)
Chat messages partial:              200 (HTMX target)
Chat send (POST):                   200 (yangi message-list HTML)
Customer chat room (ishtirokchi):   200 ✓
Other user chat room:               403 ✓
Other user chat messages:           403 ✓
Other user chat send:               403 ✓
```

## Qoidalarga muvofiqlik

- ✅ **Daxlsizlik**: mavjud DRF view'lar (CheckoutView, OrderListView),
  chat services (get_or_create_direct_room, send_message) o'zgarmagan.
- ✅ **Xavfsizlik**: 3 darajali permission (LoginRequired → role → ishtirokchi
  tekshiruvi); CSRF token har bir POST'da; multipart upload toza.
- ✅ **Tushunarlilik**: barcha yangi qatorlar batafsil izoh bilan.
- ✅ **Hujjatlashtirish**: ushbu fayl + har bir fayl docstring'i.
- ✅ **README integrity**: README'ga tegmadik.
- ✅ **Vazifa cheklovlari**:
  - `apps/chat/` ustiga yozildi (services qoldirildi, views/selectors/urls to'ldirildi)
  - Migration kerak bo'lmadi (modellar avval yaratilgan)
  - `templates/chat/` papkasi yaratildi
  - `config/urls.py`'ga chat URL'lari ulandi
