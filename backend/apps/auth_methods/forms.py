"""Forms for customer registration."""
from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from apps.users.models import Role, User, Profile  # User va Profile modellari
from core.utils import slugify  # username yaratish uchun yordamchi


# Telefon raqami uchun validator: +998 bilan boshlanadigan 13 ta raqam
PHONE_VALIDATOR = RegexValidator(
    regex=r"^\+998\d{9}$",
    message="Telefon raqami '+998XXXXXXXXX' formatida bo'lishi kerak. Masalan: +998901234567"
)


class CustomerSignupForm(forms.Form):
    """
    Mijozlar uchun soddalashtirilgan ro'yxatdan o'tish formasi.

    Faqat quyidagi maydonlar majburiy:
      - first_name: Mijozning ismi
      - phone_number: Telefon raqami (format: +998XXXXXXXXX)

    Username avtomatik ravishda telefon raqami bilan bir xil qilinadi
    (plus belgisi olib tashlanadi va tozalash amalga oshiriladi).

    Rol har doim CUSTOMER bo'lib, is_staff va is_superuser FALSE saqlanadi.
    Bu mijozlar Django admin paneliga kira olmasligini ta'minlaydi.
    """
    # Mandatory fields
    first_name = forms.CharField(  # Ism maydoni
        max_length=120,
        required=True,
        label="Ism",
        widget=forms.TextInput(attrs={"placeholder": "To'liq ismingizni kiriting", "class": "form-input"}),
        error_messages={
            "required": "Ism kiritilishi shart.",
            "max_length": "Ism juda uzun (120 ta belgidan oshmasligi kerak)."
        }
    )
    phone_number = forms.CharField(  # Telefon raqami maydoni
        max_length=20,
        required=True,
        label="Telefon raqami",
        widget=forms.TextInput(attrs={"placeholder": "+998 90 123 45 67", "class": "form-input"}),
        error_messages={
            "required": "Telefon raqami kiritilishi shart.",
            "invalid": "Noto'g'ri format. Faqat O'zbekiston raqamlari (+998...) qabul qilinadi."
        }
        # Validator clean_phone_number da pasda bajariladi (bo'shliqlarni olib tashlash va format tekshirish)
    )
    password = forms.CharField(  # Parol maydoni
        label="Parol",
        required=True,
        widget=forms.PasswordInput(attrs={"placeholder": "Parol (kamida 6 ta belgi)", "class": "form-input"}),
        min_length=6,
        error_messages={
            "required": "Parol kiritilishi shart.",
            "min_length": "Parol kamida 6 ta belgidan iborat bo'lishi kerak."
        }
    )
    password_confirm = forms.CharField(  # Parolni tasdiqlash
        label="Parolni tasdiqlang",
        required=True,
        widget=forms.PasswordInput(attrs={"placeholder": "Parolni qayta kiriting", "class": "form-input"}),
        error_messages={"required": "Parolni tasdiqlash shart."}
    )

    def clean_phone_number(self):
        """
        Telefon raqamini clean qilish va standart formatga keltirish.
        1. Barcha bo'shliqlar, tire,ochiq qavslar olib tashlanadi.
        2. +998 bilan boshlanishi va undan keyin 9 ta raqam bo'lishini tekshiradi.
        3. Bandligini tekshiradi.
        Qaytarish: telefon raqami (+998 bilan)
        """
        import re  # Regular expression uchun
        phone = self.cleaned_data["phone_number"].strip()
        # Barcha bo'shliqlar, tirnoq, qavs, tire va boshqa belgilarni olib tashlash
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "").replace("_", "")
        # Endi telefon +998 bilan boshlanishi kerak; + ni qo'shib olamiz
        if not phone.startswith("998"):
            raise ValidationError("Telefon raqami O'zbekiston formatida (+998...) bo'lishi kerak.")
        phone = "+" + phone
        # Raqamlar sonini tekshirish: +998 + 9 ta raqam = 13 ta belgi
        if not re.match(r'^\+998\d{9}$', phone):
            raise ValidationError("Telefon raqami noto'g'ri formatda. Masalan: +998901234567")
        # Telefon raqamining bandligini tekshirish
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Bu telefon raqam allaqachon ro'yxatdan o'tgan.")
        self.cleaned_data["phone_number"] = phone
        return phone

    def clean(self):
        """
        Cross-field validation: parolni tasdiqlash.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError({
                "password_confirm": "Parollar mos kelmayapti."
            })

        return cleaned_data

    def save(self, commit=True):
        """
        Foydalanuvchini yaratish (rol CUSTOMER, is_staff=False, is_superuser=False).

        Parameters:
            commit (bool): Agar True bo'lsa, foydalanuvchi darhol bazaga saqlanadi.

        Returns:
            User: Yangi yaratilgan foydalanuvchi obyekti.
        """
        phone = self.cleaned_data["phone_number"]
        first_name = self.cleaned_data["first_name"]
        password = self.cleaned_data["password"]

        # Username ni telefon raqamidan yaratish: +998 ni olib tashlash, tozalash
        # Masalan: +998901234567 -> 901234567
        base_username = phone.replace("+", "")
        username = slugify(base_username)  # Kichik harflar, raqamlar, chiziqcha/ pastki chiziqcha

        # User yaratish (UserManager.create_user orqali)
        # create_user avtomatik tarzda role=CUSTOMER, is_staff=False, is_superuser=False qo'yadi
        user = User.objects.create_user(
            email=None,  # Email ixtiyoriy, mijozda bo'lmasa ham bo'ladi
            phone=phone,
            password=password,
            username=username,
            role=Role.CUSTOMER,  # Majburiy CUSTOMER rol
            first_name=first_name,
            # is_staff va is_superuser create_user da allaqachon False qilib belgilangan
        )

        # Foydalanuvchi uchun bo'sh Profile yaratish (profile_erp.html talab qiladi)
        Profile.objects.create(user=user)

        return user
