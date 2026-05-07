"""Views for the `showroom` app — Django Templates.

Daxlsizlik eslatma: mavjud `showroom_view` (3D Showroom) o'zgartirilmagan.
Faylning oxiriga yangi `PortfolioEditView` (CBV) qo'shildi —
sotuvchi o'z portfolio elementlarini boshqarishi uchun.
"""
from __future__ import annotations  # Type hint sintaksisi

from django.template.response import TemplateResponse

# Yangi importlar — PortfolioEditView CBV uchun
from django.contrib import messages  # success/error xabarlari
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin  # Login + role tekshiruvi
from django.shortcuts import redirect  # Form valid bo'lsa redirect uchun
from django.views.generic import TemplateView  # Asosiy CBV

# Model va forma (yangi)
from .models import PortfolioItem
from .forms import PortfolioForm


def showroom_view(request):
    """
    Bittada Premium 3D Showroom.
    Renders high-quality 3D models using Google Model-Viewer.
    """
    context = {
        "base_template": "base_erp.html",
        "categories": [
            {"id": "kitchen", "name": "Oshxona"},
            {"id": "living", "name": "Yashash xonasi"},
            {"id": "office", "name": "Ofis"},
        ],
        "demo_models": [
            {
                "id": 1,
                "name": "Premium Sheen Chair",
                "category": "living",
                "src": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/SheenChair/glTF-Binary/SheenChair.glb",
                "price": "1,200,000 so'm"
            },
            {
                "id": 2,
                "name": "Modern Table",
                "category": "office",
                "src": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/AntiqueCamera/glTF-Binary/AntiqueCamera.glb", # Placeholder
                "price": "2,500,000 so'm"
            }
        ]
    }
    return TemplateResponse(request, "showroom_erp.html", context)


# ============================================================================
# YANGI: Portfolio CRUD — sotuvchi o'z ishlarini boshqaradi
# ────────────────────────────────────────────────────────────────────────────
# URL: /portfolio/edit/  →  PortfolioEditView (LoginRequired + seller role)
#
# Funksiya:
#  GET   → mavjud portfolio elementlar ro'yxati + bo'sh formani ko'rsatadi
#  POST  → yangi PortfolioItem yaratadi (rasm upload bilan)
#  POST  delete=<uuid>  → mavjud elementni o'chiradi (faqat o'ziniki)
#
# Saqlash muvaffaqiyatli bo'lganda → /portfolio/<username>/ ga redirect.
# ============================================================================


class PortfolioEditView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    `/portfolio/edit/` — sotuvchining o'z portfoliosini boshqaruv sahifasi.

    Permission qoidalari:
    - LoginRequiredMixin: anonimlar /login/ ga
    - UserPassesTestMixin: faqat sotuvchi/internal_supplier kira oladi
      (mijoz `redirect` /profile/ ga + warning xabar)

    UI:
    - Joriy portfolio elementlar ro'yxati (rasm thumbnail + o'chirish)
    - Pastda yangi qo'shish formasi
    """

    template_name = "portfolio/edit.html"  # Yangi yaratiladi
    login_url = "/login/"  # LoginRequired uchun

    def test_func(self) -> bool:  # type: ignore[override]
        """User sotuvchimi tekshirish (UserPassesTestMixin talab qiladi)."""
        # is_seller — User modelidagi @property (role IN {SELLER, INTERNAL_SUPPLIER})
        return getattr(self.request.user, "is_seller", False)

    def handle_no_permission(self):  # type: ignore[no-untyped-def]
        """Permission fail: anonim → /login/, mijoz → /profile/."""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()  # /login/?next=...
        # Tizimga kirgan, lekin sotuvchi emas
        messages.warning(self.request, "Portfolio faqat sotuvchilar uchun.")
        return redirect("profile")  # apps/products/urls.py'dagi 'profile' nom

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        """Templatga: forma + mavjud elementlar."""
        ctx = super().get_context_data(**kwargs)
        # Yangi yaratish formasi (POST muvaffaqiyatsiz bo'lsa, ctx['form'] qaytadan to'ldiriladi)
        if "form" not in ctx:
            ctx["form"] = PortfolioForm()
        # Mavjud portfolio elementlar (faqat o'ziniki)
        ctx["items"] = PortfolioItem.objects.filter(seller=self.request.user).order_by("order", "-created_at")
        # Sahifa sarlavhasi
        ctx["page_title"] = "Portfolioni tahrirlash"
        # Public profile URL (saqlangandan keyin redirect uchun template'da link)
        ctx["public_url"] = f"/portfolio/{self.request.user.username}/"
        return ctx

    def post(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        """POST: yangi qo'shish yoki o'chirish."""
        # 1) O'chirish — POST 'delete' bo'lsa
        delete_id = request.POST.get("delete")
        if delete_id:
            # Faqat o'zining elementini o'chira oladi (xavfsizlik filter)
            deleted_count, _ = PortfolioItem.objects.filter(
                pk=delete_id, seller=request.user
            ).delete()
            if deleted_count:
                messages.success(request, "Portfolio elementi o'chirildi.")
            else:
                messages.warning(request, "Element topilmadi yoki sizga tegishli emas.")
            return redirect("portfolio:edit")

        # 2) Yangi qo'shish — formani validatsiya qilish
        form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            # `commit=False` — DB'ga yozmasdan obyektni olib, seller'ni qo'lda o'rnatish
            item = form.save(commit=False)
            item.seller = request.user  # Xavfsizlik: seller'ni avtomatik o'rnatamiz
            item.save()  # Endi DB'ga yoziladi
            messages.success(request, f"\"{item.title}\" portfolio elementi qo'shildi.")
            # Saqlashda → /portfolio/<username>/ ga redirect (vazifa talabi)
            return redirect("portfolio:detail", username=request.user.username)

        # 3) Form noto'g'ri — qaytadan render qilamiz, xato matnlari bilan
        ctx = self.get_context_data(**kwargs)
        ctx["form"] = form  # Validation xatoli forma
        return self.render_to_response(ctx)
