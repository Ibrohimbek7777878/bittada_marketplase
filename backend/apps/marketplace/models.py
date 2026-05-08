# apps/marketplace/models.py — Marketplace domeni: savatcha + saqlangan e'lonlar.
# README qoidalari: har bir qator komment, mavjud kodga zarar yetkazmaslik.
# Cart va CartItem — eski versiyada ishlagan, ularga TEGMAYMIZ — faqat optimallashtirish va SavedProduct qo'shamiz.
from __future__ import annotations  # Type hint larni kechiktirilgan baholash — sirkulyar import ehtiyoti.

from django.db import models  # Django ORM asosi.
from django.conf import settings  # AUTH_USER_MODEL ga dinamik ishora qilish uchun.

from core.models import BaseModel  # Loyihaning UUID + timestamps bazaviy modeli.


# ---------------------------------------------------------------------------
# Cart — foydalanuvchi savatchasi (eski model, o'zgarmaydi).
# ---------------------------------------------------------------------------
class Cart(BaseModel):
    """
    Har bir foydalanuvchining bitta savatchasi bo'ladi (OneToOne).
    `total_price` xususiyati — barcha CartItem.subtotal yig'indisini qaytaradi.
    """
    # Foydalanuvchi bilan bir-birga (1:1) bog'lanish — bir foydalanuvchi bitta savatcha.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # users.User modeliga dinamik ishora.
        on_delete=models.CASCADE,  # Foydalanuvchi o'chsa, savatcha ham o'chadi.
        related_name="cart",  # user.cart orqali olish.
        verbose_name="Foydalanuvchi"
    )

    class Meta:
        db_table = "marketplace_cart"  # DB jadval nomi — boshqa apps bilan to'qnashuvni oldini oladi.
        verbose_name = "Savatcha"  # Admin paneldagi yakka nom.
        verbose_name_plural = "Savatchalar"  # Admin paneldagi ko'plik nom.

    def __str__(self) -> str:
        # str() chaqirilganda ko'rinadigan nom — debug uchun foydali.
        return f"{self.user.username} savatchasi"

    @property
    def total_price(self):
        """
        Savatchadagi hamma elementlarning umumiy narxi.
        Diqqat: bu xususiyat har chaqirilganda barcha items ni yuklab oladi.
        Performance uchun view'da prefetch_related('items__product') ishlatish tavsiya etiladi.
        """
        # Generator orqali barcha subtotal larni jamlaymiz — None fallback bilan.
        return sum(item.subtotal for item in self.items.all())


# ---------------------------------------------------------------------------
# CartItem — savatchadagi har bir mahsulot satri (eski model, o'zgarmaydi).
# ---------------------------------------------------------------------------
class CartItem(BaseModel):
    """
    Savatcha ichidagi bitta mahsulot yozuvi.
    Bir cart'da bir mahsulot uchun bittadan ko'p CartItem bo'lmasligi kerak — keyingi optimallashtirishda unique constraint qo'shiladi.
    """
    # Qaysi savatchaga tegishli — CASCADE bilan birga o'chiriladi.
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,  # Savatcha o'chsa, items ham o'chadi.
        related_name="items",  # cart.items.all() orqali olish.
        verbose_name="Savatcha"
    )
    # Mahsulot — apps.products.Product ga string orqali ishora (sirkulyar importni oldini oladi).
    product = models.ForeignKey(
        "products.Product",  # String reference — Product import qilish shart emas.
        on_delete=models.CASCADE,  # Mahsulot o'chsa, savatcha elementi ham o'chadi.
        related_name="cart_items",  # product.cart_items.all() orqali olish.
        verbose_name="Mahsulot"
    )
    # Miqdor — kamida 1 bo'lishi kerak; PositiveIntegerField 0 va undan katta qabul qiladi.
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdori")

    class Meta:
        db_table = "marketplace_cart_item"
        verbose_name = "Savatcha elementi"
        verbose_name_plural = "Savatcha elementlari"

    def __str__(self) -> str:
        # Mahsulot nomi va miqdorini birga ko'rsatamiz — admin va debugda foydali.
        return f"{self.product.title_uz} x {self.quantity}"

    @property
    def subtotal(self):
        """
        Mahsulot narxi * miqdor.
        Diqqat: self.product orqali murojaat qilish N+1 query keltirib chiqaradi
        agar queryset prefetch_related('product') bilan optimallashtirilmagan bo'lsa.
        """
        return self.product.price * self.quantity


# ---------------------------------------------------------------------------
# SavedProduct — foydalanuvchi saqlagan/yoqtirgan mahsulotlar (Wishlist).
# ---------------------------------------------------------------------------
# Foydalanuvchi xohishlari: navbarda "save" tugmasi orqali e'lonlarni yashirin saqlash.
# Cart bilan farq: bu yerda quantity yo'q, faqat foydalanuvchi+mahsulot juftligi va vaqti.
class SavedProduct(BaseModel):
    """
    Foydalanuvchining saqlangan mahsulotlari (favorites/wishlist).

    Bitta foydalanuvchi bitta mahsulotni faqat bir marta saqlay oladi —
    UniqueConstraint orqali ta'minlanadi.
    """
    # Foydalanuvchi — kim saqlagan.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Foydalanuvchi o'chsa, saqlanganlari ham yo'qoladi.
        related_name="saved_products",  # user.saved_products.all() orqali ro'yxat olinadi.
        verbose_name="Foydalanuvchi"
    )
    # Saqlangan mahsulot — string reference, sirkulyar importni oldini oladi.
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,  # Mahsulot o'chsa, saqlangan yozuv ham o'chadi.
        related_name="saved_by_users",  # product.saved_by_users.count() orqali nechta odam saqlaganini olish.
        verbose_name="Mahsulot"
    )
    # Foydalanuvchining shaxsiy izohi — masalan "tug'ilgan kun uchun" yoki "narxni kuzatish".
    note = models.CharField(
        max_length=200,
        blank=True,  # Optional maydon.
        verbose_name="Shaxsiy izoh"
    )

    class Meta:
        db_table = "marketplace_saved_product"  # DB jadval nomi.
        verbose_name = "Saqlangan mahsulot"
        verbose_name_plural = "Saqlangan mahsulotlar"
        # Bir xil (user, product) juftligi takrorlanmasligi uchun.
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],  # Bir foydalanuvchi bir mahsulotni faqat bir marta saqlaydi.
                name="uniq_saved_product_per_user",  # Constraint nomi — Postgres da ko'rinadi.
            ),
        ]
        # Ro'yxatda eng yangilari yuqorida.
        ordering = ["-created_at"]
        # Tez-tez ishlatiladigan filtrlash uchun composite indeks.
        indexes = [
            models.Index(fields=["user", "-created_at"], name="saved_user_recent_idx"),
        ]

    def __str__(self) -> str:
        # Debug uchun foydali — kim qaysi mahsulotni saqlagani.
        return f"{self.user.username} → {self.product.title_uz}"
