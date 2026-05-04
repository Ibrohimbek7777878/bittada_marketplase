from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from .models import Cart, CartItem
from apps.products.models import Product
from apps.orders.models import Order, OrderItem

class AddToCartView(APIView):
    """
    Mahsulotni savatchaga qo'shish.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        
        # Foydalanuvchi savatchasini olish yoki yaratish
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Savatchada mahsulot bormi?
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
            
        cart_item.save()
        
        return Response({
            "message": "Mahsulot savatchaga qo'shildi",
            "cart_count": cart.items.count()
        }, status=status.HTTP_200_OK)

class CartView(APIView):
    """
    Savatchadagi mahsulotlarni ko'rish.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = []
        for item in cart.items.all():
            items.append({
                "id": item.id,
                "product_id": item.product.id,
                "product_title": item.product.title_uz,
                "price": item.product.price,
                "quantity": item.quantity,
                "subtotal": item.subtotal
            })
            
        return Response({
            "items": items,
            "total_price": cart.total_price
        })

class RemoveFromCartView(APIView):
    """
    Mahsulotni savatchadan o'chirish.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get('item_id')
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
        
        return Response({"message": "Mahsulot savatchadan o'chirildi"}, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    """
    Checkout sahifasi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
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
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.items.exists():
            return Response({"message": "Savatcha bo'sh"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Har bir sotuvchi uchun alohida buyurtma yaratish
        # Hozircha barcha mahsulotlarni bitta sotuvchi (birinchi mahsulot sotuvchisi) uchun olamiz
        # TZ bo'yicha murakkab bo'lsa, bu yerni o'zgartirish kerak
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
        cart.items.all().delete()
        
        return Response({
            "message": "Buyurtma qabul qilindi",
            "order_id": order.id,
            "redirect_url": "/orders/"
        }, status=status.HTTP_201_CREATED)
