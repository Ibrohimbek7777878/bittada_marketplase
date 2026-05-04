from django.db import models
from django.conf import settings
from core.models import BaseModel

class Cart(BaseModel):
    """
    User savatchasi modeli.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Foydalanuvchi"
    )

    class Meta:
        db_table = "marketplace_cart"
        verbose_name = "Savatcha"
        verbose_name_plural = "Savatchalar"

    def __str__(self) -> str:
        return f"{self.user.username} savatchasi"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(BaseModel):
    """
    Savatchadagi mahsulotlar.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Savatcha"
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Mahsulot"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdori")

    class Meta:
        db_table = "marketplace_cart_item"
        verbose_name = "Savatcha elementi"
        verbose_name_plural = "Savatcha elementlari"

    def __str__(self) -> str:
        return f"{self.product.title_uz} x {self.quantity}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity
