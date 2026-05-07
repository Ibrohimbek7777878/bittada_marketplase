"""
Orders views.

Daxlsizlik eslatma: ushbu fayl avval faqat DRF API'larini (CheckoutView,
OrderListView) o'z ichiga olardi. Faylning oxiriga "SELLER ORDERS" bo'limi
qo'shildi (template CBV'lar). Mavjud DRF view'larga aralashilmagan.
"""
from __future__ import annotations

from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.db import transaction
# Django CBV asoslari va auth mixin'lar (yangi seller view'lari uchun)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from apps.orders.models import Order, OrderItem, OrderStatus
from apps.orders.serializers import CheckoutSerializer, OrderSerializer
from apps.orders.selectors import get_orders_for_seller, get_order_for_user  # Yangi selektorlar
from apps.products.models import Product


class CheckoutView(views.APIView):
    """
    Handle order placement from checkout.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        items_data = data.pop("items")
        
        try:
            with transaction.atomic():
                # For simplicity in v1, we assume all items belong to one seller 
                # or we create separate orders per seller. 
                # Let's group by seller.
                
                seller_items = {}
                for item in items_data:
                    product = Product.objects.get(id=item["product_id"])
                    seller_id = product.seller_id
                    if seller_id not in seller_items:
                        seller_items[seller_id] = []
                    seller_items[seller_id].append({
                        "product": product,
                        "quantity": item["quantity"],
                        "price": product.price # In real app, consider effective_price
                    })

                created_orders = []
                for seller_id, items in seller_items.items():
                    order = Order.objects.create(
                        customer=request.user,
                        seller_id=seller_id,
                        status=OrderStatus.INQUIRY, # Initial stage
                        shipping_address=data["address"],
                        contact_phone=data["phone"],
                        notes=data.get("notes", ""),
                    )
                    
                    total_price = 0
                    for item_data in items:
                        prod = item_data["product"]
                        qty = item_data["quantity"]
                        price = item_data["price"]
                        subtotal = price * qty
                        
                        OrderItem.objects.create(
                            order=order,
                            product=prod,
                            quantity=qty,
                            unit_price=price,
                            subtotal=subtotal
                        )
                        total_price += subtotal
                    
                    order.total_price = total_price
                    order.save()
                    created_orders.append(order)

                return Response({
                    "message": "Buyurtma muvaffaqiyatli qabul qilindi",
                    "orders": OrderSerializer(created_orders, many=True).data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Customers see their own orders, sellers see orders assigned to them
        if request.user.is_seller:
            orders = Order.objects.filter(seller=request.user)
        else:
            orders = Order.objects.filter(customer=request.user)
            
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


# ============================================================================
# SELLER ORDERS — Sotuvchining buyurtma boshqaruv panelida ishlatiladigan view'lar
# ────────────────────────────────────────────────────────────────────────────
# URL'lar (apps/orders/urls.py'da `seller_order_urlpatterns` ostida):
#   /dashboard/seller/orders/                  → SellerOrderListView
#   /dashboard/seller/orders/<uuid:pk>/        → SellerOrderDetailView
#
# Daxlsizlik: bu yangi CBV'lar mavjud DRF view'lar bilan parallel ishlaydi.
# ============================================================================


class SellerOrderListView(LoginRequiredMixin, ListView):
    """
    `/dashboard/seller/orders/` — sotuvchiga kelgan barcha buyurtmalar ro'yxati.

    Permission: faqat tizimga kirgan SOTUVCHI ko'radi (LoginRequired + role tekshiruvi).
    Boshqa userlar 403/redirect oladi.
    Filterlash: status (GET ?status=...).
    Pagination: 20 ta har sahifada.
    """

    model = Order
    template_name = "dashboard/seller/orders/list.html"  # Yangi yaratiladi
    context_object_name = "orders"  # {% for o in orders %}
    paginate_by = 20  # Har sahifada 20 ta yozuv
    login_url = "/login/"  # LoginRequired uchun

    def dispatch(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        """Role tekshiruvi: faqat seller/internal_supplier."""
        # Avval LoginRequiredMixin ishlasin (tizimga kirmagan bo'lsa /login/ ga)
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        # Tizimga kirgan: rol tekshiramiz
        if not getattr(request.user, "is_seller", False):
            # Customer/admin emas — 403 Forbidden (vazifa talabi)
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Bu sahifa faqat sotuvchilar uchun.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):  # type: ignore[no-untyped-def]
        """Faqat shu sotuvchining buyurtmalari (selektor orqali)."""
        # Selektor pure-read; status filter URL'dan
        status_filter = self.request.GET.get("status", "").strip() or None
        return get_orders_for_seller(self.request.user.id, status=status_filter)

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        """Templatga sidebar va filter dropdown uchun ma'lumot."""
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "page_title": "Mening buyurtmalarim",
            "active_section": "orders",  # Sidebar aktiv link
            "status_choices": OrderStatus.choices,
            "current_status": self.request.GET.get("status", ""),
        })
        return ctx


class SellerOrderDetailView(LoginRequiredMixin, DetailView):
    """
    `/dashboard/seller/orders/<uuid:pk>/` — buyurtma detali.

    Permission: faqat order.seller yoki order.customer ko'ra oladi
    (selektor `get_order_for_user` shuni tekshiradi).
    Boshqa user — 404 (mavjudligini ham bilinmasin).
    """

    model = Order
    template_name = "dashboard/seller/orders/detail.html"  # Yangi yaratiladi
    context_object_name = "order"  # {% block %}{{ order.id }}{% endblock %}
    login_url = "/login/"

    def get_object(self, queryset=None):  # type: ignore[no-untyped-def]
        """Selektor orqali permission'siz olamiz, keyin tekshiramiz."""
        order_id = self.kwargs.get("pk")
        # get_order_for_user — agar user buyer/seller bo'lmasa None qaytaradi
        order = get_order_for_user(order_id, self.request.user)
        if order is None:
            raise Http404("Buyurtma topilmadi yoki sizga ruxsat yo'q.")
        return order

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        """Chat xonasini context'ga qo'shamiz (vazifa talabi)."""
        ctx = super().get_context_data(**kwargs)
        # Chat xonasini topamiz/yaratamiz (lazy — kerak bo'lsa)
        # Selektor: agar user buyurtma egasi bo'lsa, xonani qaytaradi
        from apps.chat.selectors import get_or_create_room_for_order
        chat_room = get_or_create_room_for_order(self.object, self.request.user)
        # Buyurtmaning boshqa ishtirokchisi (other_party) — chat sarlavhasi uchun
        if self.object.seller_id == self.request.user.id:
            other_party = self.object.customer  # Sotuvchi qarab — mijozni ko'rsatamiz
        else:
            other_party = self.object.seller  # Aksincha
        ctx.update({
            "page_title": f"Buyurtma #{str(self.object.id)[:8]}",
            "active_section": "orders",  # Sidebar aktiv link
            "chat_room": chat_room,  # Templatda link va chat preview uchun
            "other_party": other_party,  # Mijoz yoki sotuvchi (boshqa tomon)
            "is_seller_view": self.object.seller_id == self.request.user.id,  # Layout farqi uchun
        })
        return ctx
