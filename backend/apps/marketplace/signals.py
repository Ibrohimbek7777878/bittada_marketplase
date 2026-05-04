from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import OrderItem

@receiver(post_save, sender=OrderItem)
def update_stock_on_order(sender, instance, created, **kwargs):
    """
    Buyurtma yaratilganda mahsulot omboridagi (stock) sonidan buyurtma qilingan miqdorni ayirish.
    """
    if created:
        product = instance.product
        if product.stock_qty >= instance.quantity:
            product.stock_qty -= instance.quantity
            if product.stock_qty == 0:
                product.is_in_stock = False
            product.save(update_fields=['stock_qty', 'is_in_stock'])
