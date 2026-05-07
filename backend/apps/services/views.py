"""Views for `services`.

Daxlsizlik eslatma: mavjud function-based views (services_view,
service_type_detail, create_booking va h.k.) o'zgartirilmagan. Faylning
oxiriga "STANDART CARD UI" bo'limi qo'shildi (CBV'lar):
- ServiceListView: standart kartali grid sahifa
- PortfolioDetailView: `/portfolio/<username>/` — sotuvchi portfolio sahifasi
"""
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
# Yangi importlar — CBV asoslari
from django.views.generic import ListView, TemplateView
from .models import Service, ServiceBooking, ServiceBookingStatus
from . import services as svc
from .selectors import check_service_availability, get_service_next_slot

def _get_base_template(request):
    return "base_erp_htmx.html" if request.headers.get("HX-Request") else "base_erp.html"

def services_view(request):
    """Provider directory — every registered seller / supplier is listed here.

    Cards link out to the user's Instagram-style public profile at
    ``/@<username>/``. Filters: profession (master / designer / supplier /
    manufacturer) and free-text search.
    """
    from apps.users.providers import list_providers, profession_facets
    from apps.users.models import Profession

    selected_profession = (request.GET.get("profession") or "").strip()
    search = (request.GET.get("q") or "").strip()

    providers = list_providers(
        profession=selected_profession or None,
        search=search or None,
    )

    context = {
        "base_template": _get_base_template(request),
        "providers": providers,
        "profession_facets": profession_facets(),
        "selected_profession": selected_profession,
        "search": search,
        "profession_labels": dict(Profession.choices),
        "page_title": "Mutaxassislar — Bittada",
    }
    return TemplateResponse(request, "services/providers_index.html", context)

def service_type_detail(request, service_slug):
    """Xizmat turi bo'yicha mutaxassislar ro'yxati (Demo Fallback bilan)"""
    
    # 1. Slug to Category Mapping
    MAPPING = {
        'dizayn-va-loyihalash': 'Dizayn',
        'ornatish-va-yigish': 'O\'rnatish',
        'restavratsiya': 'Restavratsiya',
        'transport': 'Transport'
    }
    category_name = MAPPING.get(service_slug, service_slug.replace('-', ' ').capitalize())
    
    # 2. Query real data — prefetch for performance
    services_qs = Service.objects.filter(category=category_name, is_open_for_booking=True).prefetch_related('bookings')
    services_list = list(services_qs)
    
    # 3. Demo Fallback (5 profiles per category)
    if not services_list:
        first_names = ["Azizbek", "Murodjon", "Jaloliddin", "Sardor", "Ibrohim"]
        last_names = ["Karimov", "Aliyev", "Tursunov", "Ismoilov", "G'ofurov"]
        
        for i in range(5):
            s, _ = Service.objects.get_or_create(
                title=f"{first_names[i]} {last_names[i]} - {category_name}",
                provider=request.user if request.user.is_authenticated else None,
                category=category_name,
                defaults={
                    "rating": round(4.5 + i * 0.1, 1),
                    "review_count": 12 + i * 5,
                    "starting_price": 200000 + i * 150000,
                    "is_open_for_booking": True,
                    "description": f"{category_name} sohasida professional xizmat",
                    "price_type": "fixed",
                }
            )
            services_list.append(s)
            
    # 4. Context for UI
    all_categories = ['Barchasi', 'Dizayn', 'O\'rnatish', 'Restavratsiya', 'Transport']
    
    context = {
        "base_template": _get_base_template(request),
        "services": services_list,
        "category_name": category_name,
        "service_slug": service_slug,
        "service_categories": all_categories,
        "selected_category": category_name,
        "page_title": f"{category_name} xizmatlari"
    }
    return TemplateResponse(request, "services_erp.html", context)


@login_required
@require_POST
def create_booking(request, service_id):
    """Xizmatni band qilish — service layer orqali (double-booking himoyalangan)"""
    try:
        booking = svc.create_booking(
            service_id=service_id,
            customer=request.user,
            notes=request.POST.get('notes', ''),
        )
        return JsonResponse({
            "status": "success",
            "booking_id": booking.id,
            "message": "So'rov navbatga qo'shildi ✓",
        })
    except Service.DoesNotExist:
        return JsonResponse({"error": "Xizmat topilmadi"}, status=404)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_POST
def advance_booking(request, booking_id):
    """Buyurtma statusini keyingi bosqichga o'tkazish (provider view)"""
    try:
        booking = svc.advance_booking_status(booking_id=booking_id, actor=request.user)
        return JsonResponse({"status": "success", "new_status": booking.status})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_POST
def post_progress(request, booking_id):
    """Jonli progress oqimiga yangilanish qo'shish (provider view)"""
    try:
        booking = svc.add_progress_update(
            booking_id=booking_id,
            actor=request.user,
            text=request.POST.get('text', ''),
            photo_url=request.POST.get('photo_url', ''),
        )
        return JsonResponse({"status": "success", "feed_count": len(booking.progress_feed)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def booking_dashboard(request):
    """Mijoz uchun xizmatlar jarayonini kuzatish sahifasi"""
    bookings = (
        ServiceBooking.objects
        .filter(customer=request.user)
        .select_related('service')
        .order_by('-created_at')
    )
    context = {
        "base_template": _get_base_template(request),
        "bookings": bookings,
        "page_title": "Mening buyurtmalarim (Xizmatlar)",
    }
    return TemplateResponse(request, "services/booking_dashboard.html", context)


# ============================================================================
# YANGI: STANDART CARD UI — yangi CBV'lar
# ────────────────────────────────────────────────────────────────────────────
# Sabab: vazifa "muammo: kartalar standart emas, har bir seller uchun
# alohida portfolio sahifasi yo'q". Bu CBV'lar yangi standart shablonlarni
# (templates/services/list.html, templates/portfolio/detail.html) render
# qiladi. Mavjud function-based viewlar saqlanadi (daxlsizlik).
# ============================================================================


class ServiceListView(ListView):
    """
    Standart kartalar bilan xizmatlar grid sahifasi.

    Templates: templates/services/list.html
    Karta fragmenti: templates/services/card.html (har xizmat uchun)

    Filterlash: ?category=<value> (Service.category — TextChoices yoki erkin matn)
    Pagination: 24 ta har sahifada (4×6 grid uchun qulay).

    URL'ga ulash: foydalanuvchi xohlasa apps/services/urls.py'ga qo'shadi.
    Bu CBV o'zi mustaqil ishlaydi.
    """

    model = Service  # ListView qaysi modeldan oladi
    template_name = "services/list.html"  # Yangi standart shablon
    context_object_name = "services"  # {% for s in services %}
    paginate_by = 24  # Har sahifada 24 ta karta

    def get_queryset(self):  # type: ignore[no-untyped-def]
        """Provider bilan select_related (kartochkada avatar/username kerak)."""
        # `provider__profile` JOIN — kartada avatar ko'rsatish uchun
        qs = (
            Service.objects.filter(is_open_for_booking=True)  # Default: faqat ochiq
            .select_related("provider", "provider__profile")  # N+1 oldini olish
            .order_by("-rating", "-created_at")  # Eng yaxshi reyting yuqorida
        )
        # Optional kategoriya filter (URL'dan ?category=...)
        category = self.request.GET.get("category", "").strip()
        if category and category.lower() != "barchasi":
            # Service.category — TextChoices, lekin DB'da string saqlanadi
            qs = qs.filter(category__iexact=category)
        # Faqat ochiqlarni ko'rsatishni override qilish (?show=all)
        if self.request.GET.get("show") == "all":
            qs = Service.objects.select_related("provider", "provider__profile").order_by("-rating")
        return qs

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        """Sahifa header'i va filter dropdown ma'lumotlari."""
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "page_title": "Xizmatlar — Standart ko'rinish",
            "current_category": self.request.GET.get("category", ""),
            # Kategoriya tanlovlari — TextChoices'dan olamiz
            "category_choices": list(__import__("apps.services.models", fromlist=["ServiceCategory"]).ServiceCategory.choices),
        })
        return ctx


class PortfolioDetailView(TemplateView):
    """
    `/portfolio/<str:username>/` — sotuvchining portfolio sahifasi.

    Templates: templates/portfolio/detail.html

    Ko'rsatadi:
    - Avatar, ism (display_name yoki username), reyting (Profile.rating), joylashuv, bio
    - Portfolio elementlari grid (PortfolioItem'lar — apps/showroom/models.py)
    - Agar joriy user — owner bo'lsa, "Tahrirlash" tugmasi ko'rinadi

    Permission: ochiq sahifa (anonimlar ham ko'radi). Faqat:
    - Username topilmasa → 404
    - User customer bo'lsa → 404 (mijozlar portfolioga ega emas)
    - Profile.visibility != PUBLIC → 404
    """

    template_name = "portfolio/detail.html"

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        ctx = super().get_context_data(**kwargs)
        # URL'dan username
        username = kwargs.get("username") or self.kwargs.get("username")

        # User'ni topish (lazy import — circular oldini olish uchun)
        from apps.users.models import User, ProfileVisibility
        from apps.showroom.models import PortfolioItem

        # Username bo'yicha topish (case-insensitive — Instagram qoidasi)
        try:
            user = (
                User.objects.select_related("profile")
                .prefetch_related("profile__avatars")  # Avatar uchun N+1 oldini olish
                .get(username__iexact=username, is_active=True)
            )
        except User.DoesNotExist as exc:
            raise Http404("Foydalanuvchi topilmadi.") from exc

        # Faqat sotuvchilar (is_seller property — seller/internal_supplier)
        if not getattr(user, "is_seller", False):
            raise Http404("Bu foydalanuvchining portfoliosi yo'q.")

        # Profile mavjudmi va public ko'rinishdami
        profile = getattr(user, "profile", None)
        if profile is None or profile.visibility != ProfileVisibility.PUBLIC:
            raise Http404("Profil yashirin yoki mavjud emas.")

        # Portfolio elementlari (faqat published)
        items = (
            PortfolioItem.objects.filter(seller=user, is_published=True)
            .order_by("order", "-created_at")
        )

        # Owner aniqlash (joriy user — sahifa egasi bo'lsa "Tahrirlash" tugmasi)
        is_owner = (
            self.request.user.is_authenticated
            and self.request.user.id == user.id
        )

        ctx.update({
            "seller": user,  # Templatda {{ seller.username }}, {{ seller.email }}
            "profile": profile,  # display_name, bio, address_text, rating
            "items": items,  # Portfolio elementlari ro'yxati
            "is_owner": is_owner,  # Tahrirlash tugmasi shartiga
            "page_title": (profile.display_name or user.username) + " — Portfolio",
        })
        return ctx
