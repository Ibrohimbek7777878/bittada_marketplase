"""
Forms for `users` app — Django ModelForm wrappers.
"""
from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import (
    Profile,
    ProfileAvatar,
    ProfileVisibility,
    Role,
    User,
    USERNAME_VALIDATOR,
)


class RegisterForm(forms.Form):
    """Standart Django ro'yxatdan o'tish formasi."""
    username = forms.CharField(
        max_length=30,
        min_length=3,
        validators=[USERNAME_VALIDATOR],
        label=_("Foydalanuvchi nomi"),
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "alice-design"}),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "you@example.com"}),
    )
    password1 = forms.CharField(
        label=_("Parol"),
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": _("Kamida 8 ta belgi")}),
    )
    password2 = forms.CharField(
        label=_("Parolni tasdiqlang"),
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": _("Parolni qaytadan kiriting")}),
    )

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_("Bu username allaqachon band."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Bu email allaqachon ro'yxatdan o'tgan."))
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", _("Parollar mos kelmayapti."))
        return cleaned

    def save(self) -> User:
        cd = self.cleaned_data
        user = User.objects.create_user(
            email=cd["email"],
            password=cd["password1"],
            username=cd["username"],
            role=Role.CUSTOMER,
        )
        return user


# ─────────────────────────────────────────────────────────────────────────────
# ROLE-SPECIFIC DASHBOARD FORMS (10 Granular Forms)
# ─────────────────────────────────────────────────────────────────────────────

class BaseDashboardForm(forms.Form):
    """Base logic for all dashboard interaction forms."""
    def __init__(self, *args, user: User | None = None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def save(self):
        return True


# 1. Partners
class PartnerMaterialForm(BaseDashboardForm):
    material_name = forms.CharField(label=_("Xom-ashyo nomi"), widget=forms.TextInput(attrs={"class": "field-input"}))
    quantity = forms.IntegerField(label=_("Miqdor"), widget=forms.NumberInput(attrs={"class": "field-input"}))
    unit = forms.ChoiceField(choices=[("kg", "Kg"), ("m2", "M2"), ("pcs", "Dona")], label=_("O'lchov birligi"))

class PartnerServiceForm(BaseDashboardForm):
    service_type = forms.ChoiceField(choices=[("insurance", "Sug'urta"), ("credit", "Kredit")], label=_("Xizmat turi"))
    report_file = forms.FileField(label=_("Hisobot (PDF)"), widget=forms.ClearableFileInput(attrs={"class": "field-input"}))


# 2. Specialists
class DesignerInteriorForm(BaseDashboardForm):
    project_name = forms.CharField(label=_("Loyiha nomi"))
    style = forms.CharField(label=_("Uslub (Masalan: Loft)"))
    area_sqm = forms.IntegerField(label=_("Maydon (m2)"))

class Designer3DForm(BaseDashboardForm):
    model_name = forms.CharField(label=_("3D Model nomi"))
    poly_count = forms.CharField(label=_("Poligonlar soni"))
    format = forms.ChoiceField(choices=[("obj", "OBJ"), ("fbx", "FBX"), ("glb", "GLB")])

class FixerMasterForm(BaseDashboardForm):
    order_id = forms.CharField(label=_("Buyurtma ID"))
    tools_ready = forms.BooleanField(label=_("Uskunalar tayyormi?"), required=False)

class FixerRepairForm(BaseDashboardForm):
    damage_description = forms.Textarea(attrs={"rows": 3})
    estimated_cost = forms.DecimalField(label=_("Taxminiy xarajat"))


# 3. Sellers
class SellerRetailForm(BaseDashboardForm):
    store_name = forms.CharField(label=_("Do'kon nomi"))
    is_open = forms.BooleanField(label=_("Hozir ochiqmi?"), required=False)

class SellerManufacturerForm(BaseDashboardForm):
    factory_capacity = forms.CharField(label=_("Ishlab chiqarish quvvati"))
    lead_time = forms.IntegerField(label=_("Tayyor bo'lish muddati (kun)"))

class SellerLogisticsForm(BaseDashboardForm):
    vehicle_type = forms.CharField(label=_("Transport turi"))
    max_weight = forms.IntegerField(label=_("Maksimal yuk (kg)"))

class SellerComponentForm(BaseDashboardForm):
    part_category = forms.CharField(label=_("Qism kategoriyasi"))
    compatible_with = forms.CharField(label=_("Mos keluvchi modellar"))


# ─────────────────────────────────────────────────────────────────────────────
# LEGACY & GENERAL FORMS
# ─────────────────────────────────────────────────────────────────────────────

class SellerProfileForm(forms.Form):
    """Sotuvchining profil tahrirlash formasi (User + Profile + Avatar)."""
    username = forms.CharField(
        max_length=30,
        min_length=3,
        validators=[USERNAME_VALIDATOR],
        label=_("Username (foydalanuvchi nomi)"),
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    display_name = forms.CharField(max_length=120, required=False, label=_("Ko'rinadigan ism"), widget=forms.TextInput(attrs={"class": "form-input"}))
    bio = forms.CharField(required=False, label=_("Bio"), widget=forms.Textarea(attrs={"class": "form-input", "rows": 4}))
    address_text = forms.CharField(max_length=300, required=False, label=_("Manzil"), widget=forms.TextInput(attrs={"class": "form-input"}))
    telegram = forms.CharField(max_length=64, required=False, label=_("Telegram"), widget=forms.TextInput(attrs={"class": "form-input"}))
    website = forms.URLField(required=False, label=_("Veb-sayt"), widget=forms.URLInput(attrs={"class": "form-input"}))
    visibility = forms.ChoiceField(choices=ProfileVisibility.choices, label=_("Profil ko'rinishi"), widget=forms.Select(attrs={"class": "form-input"}))
    avatar = forms.ImageField(required=False, label=_("Avatar"))

    def __init__(self, *args, user: User | None = None, **kwargs):
        self.user = user
        if user is not None:
            profile = getattr(user, "profile", None)
            initial = kwargs.setdefault("initial", {})
            initial.setdefault("username", user.username)
            if profile is not None:
                initial.setdefault("display_name", profile.display_name)
                initial.setdefault("bio", profile.bio)
                initial.setdefault("address_text", profile.address_text)
                initial.setdefault("telegram", profile.telegram)
                initial.setdefault("website", profile.website)
                initial.setdefault("visibility", profile.visibility)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        qs = User.objects.filter(username__iexact=username)
        if self.user is not None:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError(_("Bu username allaqachon band."))
        return username

    def save(self) -> User:
        if self.user is None:
            raise RuntimeError("SellerProfileForm.save() requires user= in __init__")
        cd = self.cleaned_data
        self.user.username = cd["username"]
        self.user.save(update_fields=["username"])
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.display_name = cd.get("display_name", "")
        profile.bio = cd.get("bio", "")
        profile.address_text = cd.get("address_text", "")
        profile.telegram = cd.get("telegram", "")
        profile.website = cd.get("website", "")
        profile.visibility = cd.get("visibility", ProfileVisibility.PUBLIC)
        profile.save()
        new_avatar = cd.get("avatar")
        if new_avatar:
            ProfileAvatar.objects.filter(profile=profile, is_primary=True).update(is_primary=False)
            ProfileAvatar.objects.create(profile=profile, image=new_avatar, is_primary=True)
        return self.user


class UserUpdateForm(forms.ModelForm):
    """Foydalanuvchi asosiy ma'lumotlarini yangilash (email o'chirilgan)."""
    first_name = forms.CharField(
        max_length=80,
        required=False,
        label=_("Ism"),
        widget=forms.TextInput(attrs={"class": "field-input", "placeholder": _("Masalan: Azizbek")}),
    )

    class Meta:
        model = User
        fields = ["phone"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "field-input", "placeholder": "+998901234567"}),
        }

    def save(self, commit=True):
        user = super().save(commit=commit)
        first_name = self.cleaned_data.get("first_name", "")
        if first_name and hasattr(user, 'profile'):
            user.profile.display_name = first_name
            user.profile.save(update_fields=["display_name"])
        return user


MAX_VIDEO_SIZE_MB = 20


class ProfileUpdateForm(forms.ModelForm):
    """Profil umumiy ma'lumotlarini yangilash."""
    avatar = forms.ImageField(required=False, label=_("Avatar"))

    class Meta:
        model = Profile
        fields = [
            "display_name", "company_name", "stir", "mfo", "bank_account",
            "bio", "address_text", "telegram", "website", "visibility",
            "cover_image", "video_intro",
        ]
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "field-input", "placeholder": _("Ko'rinadigan ism")}),
            "company_name": forms.TextInput(attrs={"class": "field-input"}),
            "stir": forms.TextInput(attrs={"class": "field-input", "placeholder": "123456789"}),
            "mfo": forms.TextInput(attrs={"class": "field-input"}),
            "bank_account": forms.TextInput(attrs={"class": "field-input"}),
            "bio": forms.Textarea(attrs={"class": "field-input", "rows": 4, "placeholder": _("O'zingiz haqingizda qisqacha")}),
            "address_text": forms.TextInput(attrs={"class": "field-input", "placeholder": _("Toshkent, Chilonzor..")}),
            "telegram": forms.TextInput(attrs={"class": "field-input", "placeholder": "@username"}),
            "website": forms.URLInput(attrs={"class": "field-input", "placeholder": "https://"}),
            "visibility": forms.Select(attrs={"class": "field-input"}),
            "cover_image": forms.ClearableFileInput(attrs={"class": "field-input", "accept": "image/*"}),
            "video_intro": forms.ClearableFileInput(attrs={"class": "field-input", "accept": "video/*"}),
        }

    def clean_video_intro(self):
        video = self.cleaned_data.get("video_intro")
        if video and hasattr(video, 'size'):
            max_bytes = MAX_VIDEO_SIZE_MB * 1024 * 1024
            if video.size > max_bytes:
                raise forms.ValidationError(
                    _(f"Video hajmi {MAX_VIDEO_SIZE_MB}MB dan oshmasligi kerak. Joriy hajm: {video.size // (1024*1024)}MB")
                )
        return video

    def save(self, commit=True):
        profile = super().save(commit=commit)
        avatar_file = self.cleaned_data.get('avatar')
        if avatar_file and not isinstance(avatar_file, (str, bool)):
            ProfileAvatar.objects.filter(profile=profile, is_primary=True).update(is_primary=False)
            ProfileAvatar.objects.create(profile=profile, image=avatar_file, is_primary=True)
        return profile
