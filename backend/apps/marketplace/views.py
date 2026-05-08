from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import render
from django.db import transaction

from core.exceptions import DomainError
from .selectors import get_user_cart_selector
from .services import (
    add_to_cart_service, 
    remove_from_cart_service, 
    clear_cart_service,
    update_cart_item_quantity_service
)
from apps.orders.models import Order, OrderItem

class AddToCartView(APIView):
    """
    Mahsulotni savatchaga qo'shish.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            cart_item = add_to_cart_service(user=request.user, product_id=product_id, quantity=quantity)
            return Response({
                "success": True,
                "message": "Mahsulot savatchaga qo'shildi",
                "cart_count": cart_item.cart.items.count()
            }, status=status.HTTP_200_OK)
        except DomainError as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CartView(APIView):
    """
    Savatchadagi mahsulotlarni ko'rish.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart = get_user_cart_selector(user=request.user)
        items = []
        for item in cart.items.all():
            items.append({
                "id": item.id,
                "product_id": item.product.id,
                "product_title": item.product.title_uz,
                "price": item.product.price,
                "quantity": item.quantity,
                "subtotal": item.subtotal,
                "image": item.product.images.first().image.url if item.product.images.exists() else None
            })
            
        return Response({
            "items": items,
            "total": cart.total_price,  # Yangi talab: total
            "count": cart.items.count(), # Yangi talab: count
            "total_price": cart.total_price # Backward compatibility
        })

class RemoveFromCartView(APIView):
    """
    Mahsulotni savatchadan o'chirish (POST usuli - legacy/sodda).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get('item_id')
        try:
            remove_from_cart_service(user=request.user, item_id=item_id)
            return Response({"success": True, "message": "Mahsulot savatchadan o'chirildi"}, status=status.HTTP_200_OK)
        except DomainError as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CartItemDetailView(APIView):
    """
    Savatchadagi element bilan ishlash (PATCH, DELETE).
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({"success": False, "message": "Miqdor ko'rsatilmadi"}, status=400)
        
        try:
            item = update_cart_item_quantity_service(user=request.user, item_id=pk, quantity=int(quantity))
            cart = get_user_cart_selector(request.user)
            return Response({
                "success": True,
                "quantity": item.quantity if item else 0,
                "subtotal": item.subtotal if item else 0,
                "total": cart.total_price,
                "count": cart.items.count(),
                "total_price": cart.total_price
            })
        except DomainError as e:
            return Response({"success": False, "message": str(e)}, status=400)

    def delete(self, request, pk):
        try:
            remove_from_cart_service(user=request.user, item_id=pk)
            cart = get_user_cart_selector(request.user)
            return Response({
                "success": True, 
                "message": "O'chirildi",
                "total": cart.total_price,
                "count": cart.items.count(),
                "total_price": cart.total_price
            })
        except DomainError as e:
            return Response({"success": False, "message": str(e)}, status=400)

class CheckoutView(APIView):
    """
    Checkout sahifasi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart = get_user_cart_selector(user=request.user)
        context = {
            "cart": cart,
            "user": request.user,
            "total_price": cart.total_price
        }
        return render(request, "checkout_erp.html", context)

class CreateOrderView(APIView):
    """
    Buyurtma yaratish API.
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart = get_user_cart_selector(user=request.user)
        if not cart.items.exists():
            return Response({"success": False, "message": "Savatcha bo'sh"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Sotuvchini aniqlash (birinchi mahsulotdan)
        first_item = cart.items.first()
        seller = first_item.product.seller
        
        order = Order.objects.create(
            customer=request.user,
            seller=seller,
            total_price=cart.total_price,
            contact_phone=request.data.get('phone', request.user.phone or ''),
            shipping_address=request.data.get('address', '')
        )
        
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price,
                subtotal=item.subtotal
            )
            
        # Savatchani tozalash
        clear_cart_service(user=request.user)
        
        return Response({
            "success": True,
            "message": "Buyurtma qabul qilindi",
            "order_id": order.id,
            "redirect_url": "/orders/"
        }, status=status.HTTP_201_CREATED)
