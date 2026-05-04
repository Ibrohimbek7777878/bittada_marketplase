"""Views for `services`."""
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Service, ServiceBooking, ServiceBookingStatus
from . import services as svc
from .selectors import check_service_availability, get_service_next_slot

def _get_base_template(request):
    return "base_erp_htmx.html" if request.headers.get("HX-Request") else "base_erp.html"

def services_view(request):
    """Barcha xizmatlar sahifasi — demo auto-seed with real ORM objects."""
    selected_category = request.GET.get('category', 'Barchasi')

    DEMO_CATEGORIES = ['Dizayn', "O'rnatish", 'Restavratsiya', 'Transport']
    FIRST_NAMES = ["Azizbek", "Murodjon", "Jaloliddin", "Sardor", "Ibrohim"]
    LAST_NAMES  = ["Karimov", "Aliyev", "Tursunov", "Ismoilov", "G'ofurov"]

    # Auto-seed if database is empty
    if not Service.objects.exists():
        for cat in DEMO_CATEGORIES:
            for i, (fn, ln) in enumerate(zip(FIRST_NAMES, LAST_NAMES)):
                Service.objects.get_or_create(
                    title=f"{fn} {ln} - {cat}",
                    provider=request.user if request.user.is_authenticated else None,
                    category=cat,
                    defaults={
                        "rating": round(4.5 + i * 0.1, 1),
                        "review_count": 10 + i * 4,
                        "starting_price": 150000 + i * 100000,
                        "is_open_for_booking": i % 4 != 3,   # every 4th is "band"
                        "description": f"{cat} sohasida professional xizmat",
                        "price_type": "fixed",
                    }
                )

    if selected_category == 'Barchasi':
        services = Service.objects.filter(is_open_for_booking=True).order_by('-rating')
    else:
        services = Service.objects.filter(
            category=selected_category, is_open_for_booking=True
        ).order_by('-rating')

    all_categories = ['Barchasi'] + DEMO_CATEGORIES

    context = {
        "base_template": _get_base_template(request),
        "services": services,
        "service_categories": all_categories,
        "selected_category": selected_category,
        "page_title": "Barcha xizmatlar",
    }
    return TemplateResponse(request, "services_erp.html", context)

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
