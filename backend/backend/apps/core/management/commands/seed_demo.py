import uuid
from django.core.management.base import BaseCommand
from apps.products.models import Product, Category, ProductType, ProductStatus
from apps.users.models import User
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Seeds the database with high-fidelity Bittada demo data."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # 1. Categories
        furniture_cat, _ = Category.objects.get_or_create(name_uz="Mebellar", slug="furniture")
        yotoq_cat, _ = Category.objects.get_or_create(name_uz="Yotoqxona", slug="yotoqxona", parent=furniture_cat)
        oshxona_cat, _ = Category.objects.get_or_create(name_uz="Oshxona", slug="oshxona", parent=furniture_cat)
        ofis_cat, _ = Category.objects.get_or_create(name_uz="Ofis", slug="ofis", parent=furniture_cat)
        
        mfg_cat, _ = Category.objects.get_or_create(name_uz="Ishlab chiqarish", slug="manufacturing_cat")
        xom_ashyo_cat, _ = Category.objects.get_or_create(name_uz="Xom-ashyo", slug="xom-ashyo", parent=mfg_cat)
        furnitura_cat, _ = Category.objects.get_or_create(name_uz="Furnitura", slug="furnitura", parent=mfg_cat)

        # 2. Users (Sellers/Masters)
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user, _ = User.objects.get_or_create(username="admin", is_staff=True, is_superuser=True)
            admin_user.set_password("admin123")
            admin_user.save()

        # 3. Furniture (Retail)
        retail_data = [
            ("Royal Sleep Ortopedik karavoti", 8500000, yotoq_cat),
            ("Modern Minimalist Stol to'plami", 4200000, oshxona_cat),
            ("ErgoPro Ergonomik ish kursi", 1850000, ofis_cat),
        ]
        
        for title, price, cat in retail_data:
            Product.objects.get_or_create(
                title_uz=title,
                slug=slugify(title),
                category=cat,
                seller=admin_user,
                price=price,
                product_type=ProductType.STANDARD,
                status=ProductStatus.PUBLISHED,
                stock_qty=10,
                is_in_stock=True
            )

        # 4. Manufacturing (B2B)
        mfg_data = [
            ("Kastamonu MDF Plita 18mm", 450000, xom_ashyo_cat, 50, 5),
            ("Blum Soft-Close Ilgak", 12000, furnitura_cat, 1000, 7),
        ]
        
        for title, price, cat, moq, days in mfg_data:
            Product.objects.get_or_create(
                title_uz=title,
                slug=slugify(title),
                category=cat,
                seller=admin_user,
                price=price,
                min_price=price,
                max_price=price * 1.5,
                moq=moq,
                production_time_days=days,
                product_type=ProductType.MANUFACTURING,
                status=ProductStatus.PUBLISHED,
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded  Bittada demo data!"))
