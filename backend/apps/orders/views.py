from __future__ import annotations

from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.db import transaction
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.orders.serializers import CheckoutSerializer, OrderSerializer
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
