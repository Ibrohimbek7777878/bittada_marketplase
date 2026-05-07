"""
Forms for `products` app — Django ModelForm wrappers.

Hozircha bitta forma: `ProductForm`. Sotuvchi panelidagi
"yangi mahsulot qo'shish" va "tahrirlash" sahifalarida ishlatiladi
(`/dashboard/seller/products/add/` va `.../edit/`).

Daxlsizlik: bu yangi fayl. Mavjud `apps.auth_methods.forms.CustomerSignupForm`
va boshqa formalarga ta'sir qilmaydi. `Product` modeliga ham hech qanday
yangi maydon qo'shilmaydi — faqat formdan keladigan ma'lumotlar standart
ORM orqali yoziladi.
"""
from __future__ import annotations  # Type hint sintaksisi (str literal)

# Django'ning forma asosiy moduli (forms.ModelForm, forms.ImageField, ...)
from django import forms
# i18n yordamchisi — tarjima qilinishi mumkin matnlar uchun
from django.utils.translation import gettext_lazy as _

# Mahsulot va kategoriya modellari — ModelForm shu modellarga bog'lanadi
from .models import Category, Product, ProductStatus, ProductType


class ProductForm(forms.ModelForm):  # ModelForm — Product modelining maydonlariga avtomatik moslanadi
    """
    Sotuvchi tomonidan to'ldiriladigan mahsulot formasi.

    Asosiy maydonlar (Product modelidan):
    - title_uz, description_uz: matnli ma'lumot (uz tilida — TZ defaultlari)
    - category: ForeignKey (faqat is_active=True kategoriyalar tanlanadi)
    - price: Decimal narx (so'm)
    - product_type: standart yoki manufacturing
    - status: nashr holati (default: DRAFT — keyin sotuvchi published qiladi)
    - stock_qty: zaxira soni (standard mahsulotlar uchun)

    Qo'shimcha (model'da emas, faqat formada):
    - image: ImageField — yuklangan rasm view ichida ProductImage qatori
      sifatida saqlanadi. Modelga yangi maydon qo'shilmagan.
    """

    # === ModelForm tashqarida qo'shimcha maydon: rasm upload ===
    # Bu maydon Product.images (related, ProductImage) ga view ichida joylanadi
    image = forms.ImageField(
        required=False,  # Tahrir vaqtida rasmni qayta yuklash shart emas
        label=_("Rasm"),  # Form label (UZ)
        help_text=_("PNG/JPG, maks 10 MB. Birinchi yuklangan rasm asosiy bo'ladi."),  # Yordamchi matn
        widget=forms.ClearableFileInput(attrs={  # Standart fayl-tanlash widget'i
            "accept": "image/*",  # Brauzerda faqat rasm tanlanishi uchun (UX)
            "class": "form-input",  # base.html dagi CSS klassi
        }),
    )

    class Meta:  # ModelForm konfiguratsiyasi
        model = Product  # Form qaysi modelga bog'lanadi
        # Modelning qaysi maydonlari avtomatik qo'shiladi (xavfsizlik: faqat ko'rsatilganlari)
        fields = (
            "title_uz",  # Mahsulot nomi (uz)
            "description_uz",  # Tavsif (uz)
            "category",  # FK kategoriya
            "price",  # Joriy narx
            "product_type",  # Tur (standard/manufacturing)
            "status",  # Holati (draft/published/archived)
            "stock_qty",  # Zaxira
        )
        # Har bir maydon uchun widget va atributlar (Bootstrap'siz, base.html CSS klasslari)
        widgets = {
            "title_uz": forms.TextInput(attrs={"class": "form-input", "placeholder": _("Masalan: Yotoqxona karavoti")}),
            "description_uz": forms.Textarea(attrs={"class": "form-input", "rows": 5, "placeholder": _("Mahsulot haqida batafsil...")}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "price": forms.NumberInput(attrs={"class": "form-input", "min": "0", "step": "1000"}),
            "product_type": forms.Select(attrs={"class": "form-input"}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "stock_qty": forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
        }
        # Xush ko'rinishli labellar
        labels = {
            "title_uz": _("Mahsulot nomi"),
            "description_uz": _("Tavsif"),
            "category": _("Kategoriya"),
            "price": _("Narx (so'm)"),
            "product_type": _("Mahsulot turi"),
            "status": _("Holati"),
            "stock_qty": _("Zaxira (dona)"),
        }

    def __init__(self, *args, **kwargs):  # Form initsializatsiyasi (queryset filterlash uchun)
        # Standart ModelForm konstruktoriga argumentlarni uzatamiz
        super().__init__(*args, **kwargs)
        # category dropdown'ida faqat faol kategoriyalarni ko'rsatamiz
        # Default (Category.objects.all()) o'rniga faqat is_active=True'larni
        self.fields["category"].queryset = Category.objects.filter(is_active=True).order_by("sort_order")
        # status maydoni xavfsizligi: super_admin emas user "rejected"/"archived" tanlolmasin
        # Faqat draft va published — sotuvchi o'zi nazorat qiladigan holatlar
        self.fields["status"].choices = [
            (ProductStatus.DRAFT, _("Qoralama")),
            (ProductStatus.PUBLISHED, _("Faol (nashr etilgan)")),
        ]

    def clean_price(self):  # `price` maydoni uchun maxsus validatsiya
        # Form'dan tozalangan qiymatni olamiz
        price = self.cleaned_data.get("price")
        # 0 dan kichik bo'lmasligi kerak — ModelField'da MinValueValidator bor, lekin form darajasida ham
        if price is not None and price < 0:
            raise forms.ValidationError(_("Narx 0 dan kichik bo'lmasligi kerak."))
        return price  # Qiymatni qaytarib yuboramiz (cleaned_data ichiga yoziladi)
