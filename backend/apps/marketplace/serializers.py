"""DRF serializers for `marketplace`."""
from __future__ import annotations

from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title_uz', read_only=True)
    price = serializers.DecimalField(source='product.price', read_only=True, max_digits=12, decimal_places=2)
    image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product_title', 'price', 'quantity', 'subtotal', 'image']
        read_only_fields = ['id', 'subtotal', 'product_title', 'price', 'image']

    def get_image(self, obj):
        if obj.product.images.exists():
            image_obj = obj.product.images.first()
            return image_obj.image.url if image_obj.image else None
        return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['items', 'total_price', 'count']

    def get_count(self, obj):
        return obj.items.count()


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Miqdor kamida 1 bo'lishi kerak.")
        return value
