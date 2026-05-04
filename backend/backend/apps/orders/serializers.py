from __future__ import annotations

from rest_framework import serializers
from apps.orders.models import Order, OrderItem
from apps.products.models import Product, ProductVariant


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "variant", "quantity", "unit_price", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "customer", "seller", "status", "total_price", 
            "shipping_address", "contact_phone", "notes", "items", "created_at"
        ]


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer for creating an order from the checkout page.
    """
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=500)
    payment_method = serializers.CharField(max_length=20)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    # Items are derived from the cart in the frontend, but sent for validation
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )

    def validate_items(self, items):
        for item in items:
            product_id = item.get("product_id")
            if not product_id:
                raise serializers.ValidationError("product_id is required for each item")
            
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product {product_id} not found")
            
            # MOQ validation
            qty = item.get("quantity", 1)
            if qty < product.moq:
                raise serializers.ValidationError(f"{product.title_uz} uchun minimal buyurtma: {product.moq}")
                
        return items
