"""
Business logic for `products`.

Functions in this module mutate state. They should:
- accept primitive args + the actor user;
- run inside a transaction when touching multiple rows;
- raise `core.exceptions.DomainError` on rule violations;
- emit notifications/Celery tasks rather than inline I/O.
"""
from __future__ import annotations

from django.db import transaction
from .models import Product

def increment_product_view_count_service(*, product: Product) -> None:
    """Mahsulot ko'rilishlar sonini xavfsiz oshirish."""
    # update_fields ishlatish lock-lar sonini kamaytiradi
    product.view_count += 1
    product.save(update_fields=['view_count'])

@transaction.atomic
def update_product_stock_service(*, product: Product, quantity_change: int) -> Product:
    """Zaxirani yangilash va is_in_stock bayrog'ini tekshirish."""
    product.stock_qty += quantity_change
    if product.stock_qty < 0:
        product.stock_qty = 0
    
    product.is_in_stock = product.stock_qty > 0
    product.save(update_fields=['stock_qty', 'is_in_stock'])
    return product
