from django.db.models import QuerySet
from .models import Cart

def get_user_cart_selector(user) -> Cart:
    """
    Foydalanuvchi savatchasini (optimallashtirilgan holda) qaytaradi.
    """
    cart, _ = Cart.objects.prefetch_related(
        "items__product", 
        "items__product__images"
    ).get_or_create(user=user)
    return cart
