"""Auth-flow serializers."""
from __future__ import annotations

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import authenticate  # Autentifikatsiya uchun
from django.core.exceptions import ObjectDoesNotExist  # Object topilmasa

from apps.users.models import AccountType, Role, User  # User modeli va rollar


class RegisterSerializer(serializers.Serializer): # Ro'yxatdan o'tish uchun serializer (rolga mos maydonlar bilan)
    email = serializers.EmailField( # Email maydoni
        required=False, # Majburiy emas (telefon bilan ham ro'yxatdan o'tish mumkin)
        allow_null=True, # NULL bo'lishi mumkin
        error_messages={ # Xato xabarlari
            'invalid': 'Haqiqiy email manzilingizni kiriting.', # Noto'g'ri format bo'lsa
        }
    )
    phone = serializers.CharField( # Telefon raqami maydoni
        required=False, # Majburiy emas
        allow_null=True, # NULL bo'lishi mumkin
        max_length=20, # Maksimal uzunlik 20 ta belgi
        error_messages={ # Xato xabarlari
            'max_length': 'Telefon raqami juda uzun.', # Uzun bo'lsa
        }
    )
    password = serializers.CharField( # Parol maydoni
        min_length=6, # Minimal uzunlik 6 ta belgi
        max_length=128, # Maksimal uzunlik 128 ta belgi
        write_only=True, # Faqat yozish uchun (JSON qaytganda ko'rinmaydi)
        trim_whitespace=False, # Bo'shliqlarni kesib tashlamaslik
        error_messages={ # Xato xabarlari
            'required': 'Parol kiritilishi shart.', # Kiritilmasa
            'min_length': 'Parol kamida 6 ta belgidan iborat bo\'lishi kerak.', # Qisqa bo'lsa
        }
    )
    first_name = serializers.CharField( # Ism maydoni (barcha rollar uchun)
        max_length=120, # Maksimal uzunlik
        required=True, # Majburiy maydon
        error_messages={ # Xato xabarlari
            'required': 'Ism kiritilishi shart.', # Kiritilmasa
            'blank': 'Ism bo\'sh bo\'lishi mumkin emas.', # Bo'sh bo'lsa
        }
    )
    username = serializers.RegexField( # Username maydoni (regex bilan)
        regex=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{2,29}$", # Regex qoidasi
        required=True, # Majburiy
        allow_blank=False, # Bo'sh bo'lishi mumkin emas
        error_messages={ # Xato xabarlari
            'required': 'Foydalanuvchi nomi (username) kiritilishi shart.', # Kiritilmasa
            'invalid': 'Username 3-30 ta belgidan iborat bo\'lishi kerak va harf yoki raqam bilan boshlanishi lozim.', # Noto'g'ri bo'lsa
        }
    )
    role = serializers.ChoiceField( # Foydalanuvchi roli
        choices=[Role.CUSTOMER, Role.SELLER, Role.INTERNAL_SUPPLIER], # Faqat xaridor, sotuvchi yoki ichki ta'minotchi
        default=Role.CUSTOMER, # Sukut bo'yicha xaridor
        required=False, # Majburiy emas
    )
    account_type = serializers.ChoiceField( # Hisob turi
        choices=AccountType.choices, # Individual yoki Kompaniya
        default=AccountType.INDIVIDUAL, # Sukut bo'yicha shaxsiy
        required=False, # Majburiy emas
    )
    professions = serializers.ListField( # Kasblar ro'yxati (sotuvchilar uchun - TZ 6.3)
        child=serializers.CharField(), # Har bir element matn
        required=False, # Majburiy emas
        allow_empty=True, # Bo'sh bo'lishi mumkin
    )
    company_name = serializers.CharField( # Kompaniya nomi (sotuvchilar uchun)
        max_length=200, # Maksimal uzunlik
        required=False, # Majburiy emas (faqat seller uchun talab qilinadi)
        allow_blank=True, # Bo'sh bo'lishi mumkin
    )
    experience = serializers.IntegerField( # Tajriba yillar soni (sotuvchilar uchun)
        required=False, # Majburiy emas (faqat seller uchun talab qilinadi)
        allow_null=True, # NULL bo'lishi mumkin
        min_value=0, # Minimal qiymat 0
        max_value=80, # Maksimal qiymat 80
    )
    invite_code = serializers.CharField( # Taklif kodi (ichki ta'minotchilar uchun - TZ 6.1)
        max_length=64, # Maksimal uzunlik
        required=False, # Majburiy emas (faqat internal_supplier uchun talab qilinadi)
        allow_blank=True, # Bo'sh bo'lishi mumkin
    )

    def validate(self, attrs): # Ma'lumotlarni tekshirish (cross-field validation)
        email = attrs.get('email') # Emailni olish
        phone = attrs.get('phone') # Telefonni olish
        role = attrs.get('role', Role.CUSTOMER) # Rolni olish (sukut bo'yicha customer)

        # --- XAVFSIZLIK: admin va super_admin rollari uchun ochiq register bloklash (TZ 8.2) ---
        if role in {Role.ADMIN, Role.SUPER_ADMIN}: # Agar rol admin yoki super_admin bo'lsa
            raise serializers.ValidationError( # Xato qaytarish
                "Admin va Super Admin rollari uchun ochiq ro'yxatdan o'tish mumkin emas. "
                "Ularni faqat createsuperuser yoki Admin Panel orqali yaratish mumkin."
            )

        # --- Email yoki telefon bo'lishi shart ---
        if not email and not phone: # Agar ikkalasi ham yo'q bo'lsa
            raise serializers.ValidationError("Email yoki telefon raqami kiritilishi shart.") # Xato qaytarish

        # --- Sotuvchi uchun qo'shimcha tekshiruvlar ---
        if role == Role.SELLER: # Agar rol sotuvchi bo'lsa
            if not attrs.get('professions'): # Agar kasblar tanlanmagan bo'lsa
                raise serializers.ValidationError("Sotuvchi kamida bitta mutaxassislikni tanlashi shart.") # Xato qaytarish

        # --- Ichki ta'minotchi uchun taklif kodi tekshiruvi ---
        if role == Role.INTERNAL_SUPPLIER: # Agar rol ichki ta'minotchi bo'lsa
            invite_code = attrs.get('invite_code', '') # Taklif kodini olish
            if not invite_code: # Agar taklif kodi berilmagan bo'lsa
                raise serializers.ValidationError("Ichki ta'minotchi uchun taklif kodi (Invite Code) kiritilishi shart.") # Xato qaytarish
            # Taklif kodini tekshirish (hozircha hardcoded, keyin bazadan olinadi)
            valid_invite_codes = ['BITTADA-2026-INTERNAL', 'BITTADA-INVITE-001', 'BITTADA-INVITE-002'] # Haqiqiy taklif kodlari ro'yxati
            if invite_code not in valid_invite_codes: # Agar kod ro'yxatda bo'lmasa
                raise serializers.ValidationError("Noto'g'ri taklif kodi. Iltimos, administratorga murojaat qiling.") # Xato qaytarish

        return attrs # Tekshirilgan ma'lumotlarni qaytarish


class OtpRequestSerializer(serializers.Serializer):
    target = serializers.CharField(help_text="Email or phone number")
    purpose = serializers.ChoiceField(choices=["register", "login", "reset", "verify"])
    method = serializers.ChoiceField(choices=["email_otp", "phone_otp"])


class OtpConfirmSerializer(serializers.Serializer):
    target = serializers.CharField()
    code = serializers.CharField(min_length=4, max_length=8)
    purpose = serializers.ChoiceField(choices=["register", "login", "reset", "verify"])


class BittadaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Token yaratish (login) — email yoki telefon orqali.

    Qo'shimcha: token ichida role, username, account_type ma'lumotlari qo'shiladi.
    Telefon raqami orqali ham kirish imkoniyati qo'shildi.
    """

    @classmethod
    def get_token(cls, user):  # type: ignore[override]
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        token["account_type"] = user.account_type
        return token

    def validate(self, attrs):  # type: ignore[override]
        """Email yoki telefon orqali autentifikatsiya."""
        request = self.context.get('request')
        identifier = attrs.get('email')  # Bu maydon aslida email yoki phone bo'lishi mumkin
        password = attrs.get('password')
        user = None

        # 1) Email orqali standart autentifikatsiya
        if identifier:
            user = authenticate(request=request, email=identifier, password=password)

        # 2) Agar email orqali yaroqsiz bo'lsa, telefon raqami orqali sinab ko'rish
        if user is None:
            try:
                # Telefon raqami bilan foydalanuvchini qidirish
                user_obj = User.objects.get(phone=identifier)
                # Parolni tekshirish
                if user_obj.check_password(password):
                    user = user_obj
            except ObjectDoesNotExist:
                pass

        # 3) Agar user topilmasa, xato qaytarish
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                "Bu ma'lumotlar bilan akkaunt topilmadi yoki parol noto'g'ri."
            )

        # Token yaratish (parent class get_token dan foydalanish)
        refresh = self.get_token(user)
        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {
            'id': str(user.id),
            'email': user.email,
            'username': user.username,
            'role': user.role,
            'account_type': user.account_type,
        }
        return data


class SocialLoginSerializer(serializers.Serializer):
    """Generic shape — provider decides how `credential` is interpreted."""

    provider = serializers.ChoiceField(choices=["google", "telegram"])
    credential = serializers.CharField(help_text="ID token / signed payload from the provider.")
