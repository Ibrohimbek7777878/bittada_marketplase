from django.db import transaction
from .models import Cart, CartItem
from apps.products.models import Product
from core.exceptions import DomainError

@transaction.atomic
def add_to_cart_service(user, product_id: int, quantity: int = 1) -> CartItem:
    """
    Mahsulotni savatchaga qo'shadi yoki miqdorini oshiradi.
    """
    product = Product.objects.filter(id=product_id).first()
    if not product:
        raise DomainError("Mahsulot topilmadi.")
    
    if product.stock < quantity:
        raise DomainError(f"Zaxirada yetarli mahsulot yo'q. Mavjud: {product.stock}")

    cart, _ = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
        
    cart_item.save()
    return cart_item

@transaction.atomic
def remove_from_cart_service(user, item_id: int):
    """
    Mahsulotni savatchadan o'chiradi.
    """
    cart = Cart.objects.filter(user=user).first()
    if not cart:
        raise DomainError("Savatcha topilmadi.")
        
    item = CartItem.objects.filter(id=item_id, cart=cart).first()
    if not item:
        raise DomainError("Savatcha elementi topilmadi.")
        
    item.delete()

@transaction.atomic
def clear_cart_service(user):
    """
    Savatchani tozalaydi.
    """
    cart = Cart.objects.filter(user=user).first()
    if cart:
        cart.items.all().delete()

@transaction.atomic
def update_cart_item_quantity_service(user, item_id: int, quantity: int) -> CartItem | None:
    """
    Savatchadagi mahsulot miqdorini yangilaydi.
    """
    cart = Cart.objects.filter(user=user).first()
    if not cart:
        raise DomainError("Savatcha topilmadi.")
        
    item = CartItem.objects.filter(id=item_id, cart=cart).first()
    if not item:
        raise DomainError("Savatcha elementi topilmadi.")
        
    if quantity <= 0:
        item.delete()
        return None
        
    if item.product.stock < quantity:
        raise DomainError(f"Zaxirada yetarli mahsulot yo'q. Mavjud: {item.product.stock}")
        
    item.quantity = quantity
    item.save()
    return item
