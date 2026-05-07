"""
Read queries for `orders`.

Pure functions returning querysets / dicts. No side effects, no writes.
Optimize with `select_related` / `prefetch_related` here, not in views.

Daxlsizlik eslatma: bu fayl avval faqat docstring va `from __future__`
qatoridan iborat edi. Hech qanday mavjud kodga aralashmasdan, yangi
seller dashboard view'lari uchun ikkita pure-read funksiyasi qo'shildi.
"""
from __future__ import annotations  # Type hint sintaksisi (str literal)

# Type hint uchun QuerySet
from django.db.models import QuerySet, Prefetch

# Models — Order, OrderItem va ProductImage (prefetch uchun)
from .models import Order
from apps.products.models import ProductImage  # OrderItem.product.images uchun nested prefetch


def get_orders_for_seller(
    seller_id,  # User UUID — sotuvchi
    *,  # Keyingi argumentlar — faqat nomlangan
    status: str | None = None,  # Status filter (opsional, masalan: 'paid')
) -> QuerySet[Order]:
    """
    Berilgan sotuvchiga kelgan barcha buyurtmalarni qaytaradi.

    Optimallashtirish:
    - select_related: customer (FK) — ro'yxatda mijoz nomi kerak
    - prefetch_related: items va items.product — har bir buyurtma kartasida
      qaysi mahsulot buyurtma qilingani ko'rsatiladi.

    Argumentlar:
        seller_id: User UUID (sotuvchining identifikatori)
        status: opsional OrderStatus.value (masalan, 'inquiry', 'paid')

    Qaytaradi:
        QuerySet[Order] — yangi buyurtmalar yuqorida (`-created_at`).
    """
    # Asosiy queryset — sotuvchi bo'yicha filter, mijoz JOIN
    qs = (
        Order.objects.filter(seller_id=seller_id)  # Faqat shu sotuvchining buyurtmalari
        .select_related("customer")  # FK customer (Profile uchun customer__profile ham mumkin)
        .prefetch_related(
            # items — har bir buyurtmadagi mahsulotlar; nested product__images bilan
            "items__product",  # OrderItem.product (Product) — N+1 oldini olish
            Prefetch(
                "items__product__images",  # Product.images — birinchi rasm uchun
                queryset=ProductImage.objects.filter(is_primary=True),  # Faqat primary rasm
            ),
        )
        .order_by("-created_at")  # Yangiroqlari yuqorida
    )
    # Optional status filter
    if status:  # Masalan: ?status=paid
        qs = qs.filter(status=status)
    return qs


def get_order_for_user(order_id, user) -> Order | None:
    """
    Berilgan order_id va user uchun Order'ni qaytaradi (faqat ruxsat berilgan bo'lsa).

    Permission qoidasi:
    - User Order.seller bo'lsa — ko'ra oladi
    - User Order.customer bo'lsa — ko'ra oladi
    - Boshqa hollarda — None qaytaradi (view 404 qilishi kerak)

    Argumentlar:
        order_id: Order UUID
        user: User obyekti (request.user)

    Qaytaradi:
        Order yoki None
    """
    # 1) Order topish (yo'q bo'lsa None)
    try:
        order = (
            Order.objects.select_related("customer", "seller")
            .prefetch_related("items__product__images")
            .get(pk=order_id)
        )
    except Order.DoesNotExist:
        return None

    # 2) Permission tekshiruvi: user — buyer yoki seller bo'lishi kerak
    if order.seller_id == user.id or order.customer_id == user.id:
        return order

    # Aks holda — ruxsat yo'q
    return None
