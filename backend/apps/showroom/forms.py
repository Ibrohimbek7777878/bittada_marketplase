"""
Forms for `showroom` app.

PortfolioForm — sotuvchi (usta/dizayner) o'zining bajargan ishlarini
qo'shish/tahrirlash uchun ModelForm. `apps/showroom/views.py`'dagi
`PortfolioEditView` shu formani ishlatadi.

Daxlsizlik: bu yangi fayl. Mavjud `PortfolioItem` modeli o'zgartirilmagan
(faqat formaning maydonlari shu modeldan kelib chiqadi).
"""
from __future__ import annotations  # Type hint sintaksisi (str literal)

# Django'ning forma asosiy moduli (forms.ModelForm, fields)
from django import forms
# i18n yordamchisi — tarjima qilinishi mumkin matnlar uchun
from django.utils.translation import gettext_lazy as _

# Model — apps/showroom/models.py'dagi PortfolioItem
from .models import PortfolioItem


class PortfolioForm(forms.ModelForm):  # ModelForm — PortfolioItem maydonlariga avtomatik moslanadi
    """
    Portfolio elementi (bajargan ish) qo'shish/tahrirlash formasi.

    Maydonlar (PortfolioItem modelidan):
    - title:           Ish sarlavhasi (majburiy, max 200 belgi)
    - description:     Tavsif (ixtiyoriy, ko'p qatorli)
    - cover_image:     Asosiy rasm (majburiy yangi yaratishda, ixtiyoriy edit'da)
    - location:        Joylashuv (ixtiyoriy)
    - completed_year:  Bajarilgan yili (ixtiyoriy raqam)
    - is_published:    Ko'rinishini boshqarish (default: True)

    Daxlsizlik: `seller` maydoni formada ko'rsatilmaydi — view ichida
    `request.user` dan avtomatik o'rnatiladi (xavfsizlik: foydalanuvchi
    boshqa user nomidan portfolio yarata olmaydi).
    """

    class Meta:  # Form'ni modelga bog'lash konfiguratsiyasi
        model = PortfolioItem  # Qaysi modelga bog'lanadi
        # Faqat foydalanuvchi tahrirlay oladigan maydonlar (xavfsizlik: seller, order, id chiqarib tashlandi)
        fields = (
            "title",  # Sarlavha
            "description",  # Tavsif
            "cover_image",  # Asosiy rasm
            "location",  # Joylashuv
            "completed_year",  # Bajarilgan yili
            "is_published",  # Ko'rinish (checkbox)
        )
        # Har bir maydon uchun widget atributlari (HTML class va placeholder)
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input", "placeholder": _("Masalan: Zamonaviy oshxona dizayni")}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 4, "placeholder": _("Ish haqida batafsil...")}),
            "cover_image": forms.ClearableFileInput(attrs={"accept": "image/*", "class": "form-input"}),
            "location": forms.TextInput(attrs={"class": "form-input", "placeholder": _("Toshkent, Yunusobod")}),
            "completed_year": forms.NumberInput(attrs={"class": "form-input", "min": "2000", "max": "2099", "placeholder": "2026"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }
        # Foydalanuvchi tilida tushunarli labellar
        labels = {
            "title": _("Ish sarlavhasi"),
            "description": _("Tavsif"),
            "cover_image": _("Asosiy rasm"),
            "location": _("Joylashuv"),
            "completed_year": _("Bajarilgan yili"),
            "is_published": _("Sahifada ko'rinsin"),
        }

    def clean_completed_year(self):  # Yil maydoni uchun maxsus validatsiya
        # Tozalangan qiymatni olamiz
        year = self.cleaned_data.get("completed_year")
        if year is None:  # Bo'sh — ruxsat (ixtiyoriy maydon)
            return year
        # Mantiqiy diapazon: 2000 dan oshmaslik kerak (juda qadimgi emas)
        # va kelajakdan kelgan bo'lmasligi kerak (joriy yil + 1 dan ko'p emas)
        from datetime import datetime
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 1:  # +1 — chunki yil oxirida 2027 ham mumkin
            raise forms.ValidationError(_("Yil 2000 dan {0} gacha bo'lishi mumkin.").format(current_year + 1))
        return year
