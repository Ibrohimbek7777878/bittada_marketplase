"""
Management command: reset_and_create_admin
==========================================
Barcha mavjud foydalanuvchilarni o'chirib,
yangi superadmin yaratadi.

Ishlatish:
    python manage.py reset_and_create_admin --settings=config.settings.dev
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone


class Command(BaseCommand):
    help = "Barcha foydalanuvchilarni o'chirib, yangi superadmin yaratadi"

    def handle(self, *args, **options):
        from apps.users.models import User, Profile, Role, AccountType

        # ---------------------------------------------------------------
        # 1. Barcha foydalanuvchilarni o'chirish
        # ---------------------------------------------------------------
        count = User.objects.count()
        User.objects.all().delete()
        self.stdout.write(
            self.style.WARNING(f"✓ {count} ta foydalanuvchi o'chirildi.")
        )

        # ---------------------------------------------------------------
        # 2. Superadmin yaratish
        # ---------------------------------------------------------------
        email    = "adminbittada@gmail.com"
        password = "admin123!"
        username = "adminbittada"

        # USERNAME_VALIDATOR: ^[a-zA-Z0-9][a-zA-Z0-9\s_-]{2,29}$
        # "adminbittada" — 12 ta belgi, harf bilan boshlanadi ✓

        user = User(
            email=email,
            username=username,
            role=Role.SUPER_ADMIN,
            account_type=AccountType.INDIVIDUAL,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            email_verified_at=timezone.now(),
            # Argon2 o'rniga PBKDF2 ishlatamiz (argon2-cffi majburiy emas)
            password=make_password(password, hasher="pbkdf2_sha256"),
        )
        user.save()

        # Profile yaratish (1:1 bog'liq)
        Profile.objects.create(
            user=user,
            display_name="Bittada Admin",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Superadmin muvaffaqiyatli yaratildi!\n"
                f"   Email   : {email}\n"
                f"   Parol   : {password}\n"
                f"   Username: {username}\n"
                f"\n🔗 Admin paneli: http://127.0.0.1:8000/admin/\n"
                f"🔗 Sayt login  : http://127.0.0.1:8000/login/\n"
            )
        )
