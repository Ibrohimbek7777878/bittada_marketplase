import random
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import User, Role, Profile
from apps.products.models import Product, Category, ProductType, ProductStatus
from apps.services.models import Service, ServiceCategory, ServiceBooking, ServiceBookingStatus

class Command(BaseCommand):
    help = "Seeds the database with role-specific demo data for 10 roles."

    def handle(self, *args, **options):
        self.stdout.write("Seeding role-specific data...")

        # 1. Create a Default Category for products
        category, _ = Category.objects.get_or_create(
            slug="demo-category",
            defaults={"name_uz": "Demo Kategoriya", "name_ru": "Демо Категория", "name_en": "Demo Category"}
        )

        roles_to_seed = [
            # Partners
            (Role.PARTNER_MATERIAL, "partner_material", "Material Partner LLC"),
            (Role.PARTNER_SERVICE, "partner_service", "Service Solutions Bank"),
            # Specialists
            (Role.DESIGNER_INTERIOR, "designer_interior", "Art Interior Studio"),
            (Role.DESIGNER_3D, "designer_3d", "3D Vision Studio"),
            (Role.FIXER_MASTER, "fixer_master", "Master Assembly"),
            (Role.FIXER_REPAIR, "fixer_repair", "Furniture Hospital"),
            # Sellers
            (Role.SELLER_RETAIL, "seller_retail", "Elite Furniture Store"),
            (Role.SELLER_MANUFACTURER, "seller_manufacturer", "Mega Factory"),
            (Role.SELLER_LOGISTICS, "seller_logistics", "Fast Delivery Co"),
            (Role.SELLER_COMPONENT, "seller_component", "Hardware King"),
        ]

        for role_code, username, display_name in roles_to_seed:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "role": role_code,
                    "is_active": True
                }
            )
            if created:
                user.set_password("password123")
                user.save()
            
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.display_name = display_name
            profile.company_name = display_name
            profile.save()

            self.stdout.write(f"  - User '{username}' ({role_code}) created/updated.")

            # Seed specific data based on role
            if role_code == Role.SELLER_RETAIL or role_code == Role.SELLER_MANUFACTURER or role_code == Role.SELLER_COMPONENT:
                # Create 5-10 demo products
                for i in range(5):
                    Product.objects.get_or_create(
                        slug=f"demo-product-{username}-{i}",
                        defaults={
                            "seller": user,
                            "category": category,
                            "title_uz": f"Demo Product {i} for {username}",
                            "price": random.randint(100000, 5000000),
                            "stock_qty": random.randint(1, 100),
                            "status": ProductStatus.PUBLISHED,
                            "product_type": ProductType.STANDARD if role_code != Role.SELLER_MANUFACTURER else ProductType.MANUFACTURING
                        }
                    )
            
            if role_code in [Role.DESIGNER_INTERIOR, Role.DESIGNER_3D, Role.FIXER_MASTER, Role.FIXER_REPAIR]:
                # Create a Service for the specialist
                service, _ = Service.objects.get_or_create(
                    provider=user,
                    defaults={
                        "title": f"{display_name} Services",
                        "category": self.get_service_cat(role_code),
                        "starting_price": 50000,
                        "is_open_for_booking": True
                    }
                )
                # Create some bookings
                for i in range(3):
                    ServiceBooking.objects.create(
                        service=service,
                        customer=User.objects.filter(role=Role.CUSTOMER).first() or user, # Fallback to self for demo
                        status=random.choice(ServiceBookingStatus.values),
                        agreed_price=random.randint(100000, 1000000),
                        description=f"Demo booking task {i}"
                    )

        self.stdout.write(self.style.SUCCESS("Database seeding completed!"))

    def get_service_cat(self, role):
        mapping = {
            Role.DESIGNER_INTERIOR: ServiceCategory.DESIGN,
            Role.DESIGNER_3D: ServiceCategory.DESIGN,
            Role.FIXER_MASTER: ServiceCategory.ASSEMBLY,
            Role.FIXER_REPAIR: ServiceCategory.REPAIR,
        }
        return mapping.get(role, ServiceCategory.OTHER)
