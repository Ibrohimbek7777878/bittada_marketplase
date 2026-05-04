"""
DRF Serializers for apps.management API.

Bu serializerlar ERP UI uchun moslashtirilgan — ya'ni ular sayt frontend
serializerlaridan farqli o'laroq, boshqaruv uchun zarur barcha maydonlarni
qaytaradi (sotuvchi, statistika, holat va h.k.).

Loyiha standarti: serializerlarda har bir maydon nima uchun kerakligi izohlanadi.
"""
from __future__ import annotations  # Annotatsiya kelajak rejimi

from rest_framework import serializers  # DRF asosiy moduli

from apps.orders.models import Order  # Buyurtmalar
from apps.products.models import Category, Product  # Mahsulotlar


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTS
# ─────────────────────────────────────────────────────────────────────────────

class ManagementCategoryMiniSerializer(serializers.ModelSerializer):
    """Mahsulot ichidagi kategoriya — minimal ma'lumot (id, nomi, slug)."""

    class Meta:  # DRF Meta sxemasi
        model = Category  # Manba model
        fields = ["id", "name_uz", "slug"]  # Ozod, faqat zarur maydonlar


class ManagementUserMiniSerializer(serializers.Serializer):
    """Sotuvchi/Mijoz ma'lumotlari — minimal (id, ism, email)."""
    # ModelSerializer emas, chunki User modeli ham bizga import qilishimiz kerak
    # va Serializer'da `read_only` bilan oddiyroq

    id = serializers.IntegerField(read_only=True)  # FK ID
    username = serializers.CharField(read_only=True, default="")  # Username
    email = serializers.EmailField(read_only=True, default="")  # Email
    role = serializers.CharField(read_only=True, default="")  # Rol (display uchun)


class ManagementProductSerializer(serializers.ModelSerializer):
    """Mahsulot — to'liq boshqaruv vakili.

    ERP UI dagi jadval va shakl uchun yetarli ma'lumot:
    - asosiy maydonlar (nom, sku, narx, holat)
    - relatsion maydonlar (kategoriya, sotuvchi)
    - statistika (view_count, created_at)
    """

    category_detail = ManagementCategoryMiniSerializer(source="category", read_only=True)  # Read-only nested kategoriya
    seller_detail = ManagementUserMiniSerializer(source="seller", read_only=True)  # Read-only nested sotuvchi
    primary_image_url = serializers.SerializerMethodField()  # Birinchi rasm URL'i (custom logic)

    class Meta:
        model = Product
        fields = [  # Aniq tartiblangan maydonlar ro'yxati
            "id",  # PK
            "uuid",  # Public identifikator
            "title_uz", "title_ru", "title_en",  # Nomlar
            "sku",  # Unique kod
            "price", "old_price",  # Narxlar
            "stock_qty", "is_in_stock",  # Zaxira
            "status", "product_type",  # Holat va tur
            "category",  # FK ID (yozish uchun)
            "category_detail",  # Read-only nested
            "seller",  # FK ID (yozish uchun, lekin write-da auto-fill)
            "seller_detail",  # Read-only nested
            "description_uz",  # Tavsif
            "primary_image_url",  # Birinchi rasm
            "view_count",  # Statistika
            "is_featured",  # Yulduzcha
            "created_at", "updated_at",  # Audit
        ]
        read_only_fields = ["id", "uuid", "view_count", "created_at", "updated_at"]  # Yozib bo'lmaydi

    def get_primary_image_url(self, obj: Product) -> str | None:
        """Birinchi mavjud rasm URL'i (yo'q bo'lsa None)."""
        first_image = obj.images.first()  # Mahsulotning birinchi rasmi
        if first_image and first_image.image:  # Rasm va fayli bor bo'lsa
            return first_image.image.url  # Public URL
        return None  # Rasm yo'q


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS — Savdo
# ─────────────────────────────────────────────────────────────────────────────

class ManagementOrderSerializer(serializers.ModelSerializer):
    """Buyurtma — boshqaruv uchun to'liq ma'lumot."""

    customer_detail = ManagementUserMiniSerializer(source="customer", read_only=True)  # Mijoz info
    seller_detail = ManagementUserMiniSerializer(source="seller", read_only=True)  # Sotuvchi info
    status_display = serializers.CharField(source="get_status_display", read_only=True)  # "Yangi so'rov" uslubidagi matn

    class Meta:
        model = Order
        fields = [
            "id",  # PK (#ORD-{id})
            "status",  # Mashina o'qiy oladigan kod
            "status_display",  # Inson o'qiy oladigan matn
            "customer",  # FK ID
            "customer_detail",  # Nested mijoz
            "seller",  # FK ID
            "seller_detail",  # Nested sotuvchi
            "total_price",  # Umumiy narx
            "escrow_amount",  # Escrow'da ushlangan
            "shipping_address",  # Yetkazib berish manzili
            "contact_phone",  # Aloqa telefoni
            "notes",  # Qo'shimcha izoh
            "created_at", "updated_at",  # Audit
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ─────────────────────────────────────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────────────────────────────────────

class ManagementUserSerializer(serializers.Serializer):
    """Foydalanuvchi — admin uchun ma'lumot (boshqaruv shabloni).

    Bu erda `Serializer` (ModelSerializer emas) ishlatildi — chunki User modeli
    boshqa app'da va meta-fields ko'p (password, perms va h.k.). Faqat zarur maydonlar.
    """

    id = serializers.IntegerField(read_only=True)  # PK
    username = serializers.CharField(read_only=True)  # Login nom
    email = serializers.EmailField(read_only=True)  # Email
    phone = serializers.CharField(read_only=True, default="", allow_blank=True)  # Telefon
    first_name = serializers.CharField(read_only=True, default="")  # Ism
    role = serializers.CharField(read_only=True)  # 'customer'/'seller'/'admin' va h.k.
    is_active = serializers.BooleanField()  # Bloklanmagan bo'lsa True
    is_staff = serializers.BooleanField(read_only=True)  # Bittada xodimi
    # Foydalanuvchi modelida `date_joined` o'rniga BaseModel'dan kelgan `created_at` ishlatiladi
    created_at = serializers.DateTimeField(read_only=True)  # Ro'yxatdan o'tgan vaqt
