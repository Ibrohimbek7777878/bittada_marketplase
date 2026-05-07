"""Role-based registration: per-profession sign-up forms.

The platform asks for different fields depending on who is signing up.
A master / seller only needs name + phone; a designer needs portfolio links
and specialty; a partner supplier (internal_supplier) needs a company name.

This module is self-contained — it owns its forms, its catalog of role
"meta" entries (name, icon, fields), and the views that render and submit
them. The main URL conf wires three paths:

    /register/                     → RegisterPickerView   (cards picker)
    /register/<role_slug>/         → RoleRegisterView     (form)

Slug → backend role mapping is governed by ``ROLE_CATALOG`` below.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from django import forms
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.auth_methods.services import register_with_email_password
from core.exceptions import DomainError

from .models import PHONE_VALIDATOR, Profession, Profile, Role, User, USERNAME_VALIDATOR
from .utils import get_dashboard_url


# ---------------------------------------------------------------------------
# Role catalog — drives both the picker and the per-role form fields.
# ---------------------------------------------------------------------------
@dataclass
class RoleMeta:
    slug: str
    title: str
    tagline: str
    icon: str  # bootstrap-icons class
    role: str
    professions: list[str] = field(default_factory=list)
    show_company: bool = False
    show_specialty: bool = False
    show_portfolio_url: bool = False
    show_experience: bool = False
    show_stir: bool = False
    success_message: str = ""


ROLE_CATALOG: dict[str, RoleMeta] = {
    "customer": RoleMeta(slug="customer", title=_("Mijoz"), tagline=_("Xaridlar uchun."), icon="bi-person", role=Role.CUSTOMER),
    
    # Partners
    "partner_material": RoleMeta(slug="partner_material", title=_("Xom-ashyo hamkori"), tagline=_("Materiallar yetkazib berish."), icon="bi-box-seam", role=Role.PARTNER_MATERIAL, show_company=True, show_stir=True),
    "partner_service": RoleMeta(slug="partner_service", title=_("Servis hamkori"), tagline=_("Sug'urta/Kredit xizmatlari."), icon="bi-shield-check", role=Role.PARTNER_SERVICE, show_company=True, show_stir=True),
    
    # Specialists
    "designer_interior": RoleMeta(slug="designer_interior", title=_("Interyer dizayner"), tagline=_("Dizayn xizmatlari."), icon="bi-palette", role=Role.DESIGNER_INTERIOR, show_portfolio_url=True, show_experience=True),
    "designer_3d": RoleMeta(slug="designer_3d", title=_("3D Dizayner"), tagline=_("3D modellashtirish."), icon="bi-box", role=Role.DESIGNER_3D, show_portfolio_url=True),
    "fixer_master": RoleMeta(slug="fixer_master", title=_("O'rnatuvchi usta"), tagline=_("Mebel yig'ish."), icon="bi-tools", role=Role.FIXER_MASTER, show_experience=True),
    "fixer_repair": RoleMeta(slug="fixer_repair", title=_("Ta'mirlash ustasi"), tagline=_("Mebel ta'mirlash."), icon="bi-hammer", role=Role.FIXER_REPAIR, show_experience=True),
    
    # Sellers
    "seller_retail": RoleMeta(slug="seller_retail", title=_("Chakana sotuvchi"), tagline=_("Tayyor mebel savdosi."), icon="bi-shop", role=Role.SELLER_RETAIL, show_company=True, show_stir=True),
    "seller_manufacturer": RoleMeta(slug="seller_manufacturer", title=_("Ishlab chiqaruvchi"), tagline=_("Mebel ishlab chiqarish."), icon="bi-factory", role=Role.SELLER_MANUFACTURER, show_company=True, show_stir=True),
    "seller_logistics": RoleMeta(slug="seller_logistics", title=_("Logistika"), tagline=_("Yetkazib berish xizmati."), icon="bi-truck", role=Role.SELLER_LOGISTICS, show_company=True, show_stir=True),
    "seller_component": RoleMeta(slug="seller_component", title=_("Qismlar sotuvchisi"), tagline=_("Furnitura va qismlar."), icon="bi-gear", role=Role.SELLER_COMPONENT, show_company=True, show_stir=True),
}


# ---------------------------------------------------------------------------
# Form
# ---------------------------------------------------------------------------
class RoleRegisterForm(forms.Form):
    """Profession-aware sign-up form. Fields toggle based on ``role_meta``."""

    first_name = forms.CharField(
        label=_("Ism"),
        max_length=80,
        widget=forms.TextInput(attrs={"placeholder": _("Masalan: Azizbek")}),
    )
    phone = forms.CharField(
        label=_("Telefon raqami"),
        max_length=20,
        validators=[PHONE_VALIDATOR],
        widget=forms.TextInput(attrs={"placeholder": "+998901234567"}),
    )
    password = forms.CharField(
        label=_("Parol"),
        min_length=6,
        widget=forms.PasswordInput(attrs={"placeholder": _("Kamida 6 ta belgi")}),
    )

    # Optional fields — visibility controlled per role.
    username = forms.CharField(
        label=_("Foydalanuvchi nomi (URL uchun)"),
        max_length=30,
        min_length=3,
        required=False,
        validators=[USERNAME_VALIDATOR],
        help_text=_("Profilingiz manzili: /@<username>/. Bo'sh qoldirsangiz, biz tanlaymiz."),
    )
    company_name = forms.CharField(
        label=_("Kompaniya / brend nomi"),
        max_length=200,
        required=False,
    )
    stir = forms.CharField(
        label=_("STIR (INN)"),
        max_length=20,
        required=False,
    )
    specialty = forms.CharField(
        label=_("Mutaxassislik"),
        max_length=120,
        required=False,
        help_text=_("Masalan: interyer dizayn, ofis mebellari, restoran loyihalari."),
    )
    portfolio_url = forms.URLField(
        label=_("Portfolio havolasi"),
        required=False,
        widget=forms.URLInput(attrs={"placeholder": "https://behance.net/..."}),
    )
    experience = forms.IntegerField(
        label=_("Tajriba (yil)"),
        required=False,
        min_value=0,
        max_value=80,
    )

    def __init__(self, *args, role_meta: RoleMeta, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_meta = role_meta
        # Hide fields the role does not need.
        if not role_meta.show_company:
            self.fields.pop("company_name", None)
        if not role_meta.show_stir:
            self.fields.pop("stir", None)
        if not role_meta.show_specialty:
            self.fields.pop("specialty", None)
        if not role_meta.show_portfolio_url:
            self.fields.pop("portfolio_url", None)
        if not role_meta.show_experience:
            self.fields.pop("experience", None)
        # Customer flow doesn't ask for a username — auto-derived from phone.
        if role_meta.slug == "customer":
            self.fields.pop("username", None)

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError(_("Bu telefon raqami bilan akkaunt mavjud."))
        return phone

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_("Bu username allaqachon band."))
        return username


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------
class RegisterPickerView(View):
    """choose the type of account to create."""
    template_name = "auth/register_picker.html"
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/")
        return TemplateResponse(request, self.template_name, {"roles": list(ROLE_CATALOG.values())})


class RoleRegisterView(View):
    """render and submit a single role's form."""
    template_name = "auth/register_role.html"
    def _meta(self, role_slug: str) -> RoleMeta:
        meta = ROLE_CATALOG.get(role_slug)
        if not meta: raise Http404()
        return meta
    def get(self, request, role_slug: str):
        meta = self._meta(role_slug)
        return TemplateResponse(request, self.template_name, {"role_meta": meta, "form": RoleRegisterForm(role_meta=meta)})
    def post(self, request, role_slug: str):
        meta = self._meta(role_slug)
        form = RoleRegisterForm(request.POST, role_meta=meta)
        if not form.is_valid():
            return TemplateResponse(request, self.template_name, {"role_meta": meta, "form": form}, status=400)
        cd = form.cleaned_data
        try:
            user = register_with_email_password(
                phone=cd["phone"],
                password=cd["password"],
                first_name=cd["first_name"],
                username=cd.get("username"),
                role=meta.role,
                account_type="company" if meta.show_company else "individual",
                company_name=cd.get("company_name", ""),
                stir=cd.get("stir", ""),
                experience=cd.get("experience"),
            )
            auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect(get_dashboard_url(user))
        except DomainError as e:
            form.add_error(None, str(e))
            return TemplateResponse(request, self.template_name, {"role_meta": meta, "form": form}, status=400)
