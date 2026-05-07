from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from apps.users.models import Role
from apps.users.forms import (
    PartnerMaterialForm, PartnerServiceForm,
    DesignerInteriorForm, Designer3DForm, FixerMasterForm, FixerRepairForm,
    SellerRetailForm, SellerManufacturerForm, SellerLogisticsForm, SellerComponentForm
)
from apps.products.models import Product, Category
from django.db.models import Q

# ---------------------------------------------------------------------------
# CORE DASHBOARD VIEWS (Admin Stats)
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    """Umumiy tizim statistikasi."""
    return JsonResponse({
        "status": "success", 
        "data": {
            "active_users": 105,
            "system_health": "100%",
            "server_time": "2026-05-06"
        }
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def sales_stats(request):
    """Sotuvlar statistikasi."""
    return JsonResponse({
        "status": "success",
        "data": {
            "total_sales": "1,250,000,000 UZS",
            "orders_count": 450,
            "growth": "+12%"
        }
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def products_inventory(request):
    """Invertar holati statistikasi."""
    return JsonResponse({
        "status": "success",
        "data": {
            "total_products": 1200,
            "out_of_stock": 15,
            "categories_count": 24
        }
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def services_stats(request):
    """Xizmatlar statistikasi."""
    return JsonResponse({
        "status": "success",
        "data": {
            "active_services": 85,
            "service_providers": 32
        }
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def escrow_fund(request):
    """Escrow (kafolatli to'lov) statistikasi."""
    return JsonResponse({
        "status": "success",
        "data": {
            "locked_funds": "450,000,000 UZS",
            "released_funds": "320,000,000 UZS"
        }
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def credit_economy(request):
    """Kredit ekotizimi statistikasi."""
    return JsonResponse({
        "status": "success",
        "data": {
            "active_loans": 12,
            "pending_applications": 5
        }
    })


# ---------------------------------------------------------------------------
# SELLER DASHBOARD (Interactive Logic)
# ---------------------------------------------------------------------------

def role_dashboard_router(request):
    """
    Main router for role-specific dashboards.
    Handles HTMX POST requests for role-specific actions using granular 10-role forms.
    """
    if not request.user.is_authenticated:
        return redirect("auth_login")

    user = request.user
    role = user.role

    # Initialize granular form based on role
    form_map = {
        Role.PARTNER_MATERIAL: PartnerMaterialForm,
        Role.PARTNER_SERVICE: PartnerServiceForm,
        Role.DESIGNER_INTERIOR: DesignerInteriorForm,
        Role.DESIGNER_3D: Designer3DForm,
        Role.FIXER_MASTER: FixerMasterForm,
        Role.FIXER_REPAIR: FixerRepairForm,
        Role.SELLER_RETAIL: SellerRetailForm,
        Role.SELLER_MANUFACTURER: SellerManufacturerForm,
        Role.SELLER_LOGISTICS: SellerLogisticsForm,
        Role.SELLER_COMPONENT: SellerComponentForm,
    }
    
    FormClass = form_map.get(role)
    form = FormClass(request.POST or None, user=user) if FormClass else None

    # Handle HTMX POST
    if request.method == "POST" and request.headers.get("HX-Request"):
        if form and form.is_valid():
            form.save()
            return TemplateResponse(request, "dashboard/partials/form_success.html", {"form": form})
        else:
            return TemplateResponse(request, "dashboard/partials/form_errors.html", {"form": form})

    # Template mapping
    template_name = "dashboard/profile_edit.html" # Default
    dummy_data = []

    role_templates = {
        Role.PARTNER_MATERIAL: "dashboard/partners/material.html",
        Role.PARTNER_SERVICE: "dashboard/partners/service.html",
        Role.DESIGNER_INTERIOR: "dashboard/specialists/designer_interior.html",
        Role.DESIGNER_3D: "dashboard/specialists/designer_3d.html",
        Role.FIXER_MASTER: "dashboard/specialists/fixer_master.html",
        Role.FIXER_REPAIR: "dashboard/specialists/fixer_repair.html",
        Role.SELLER_RETAIL: "dashboard/sellers/retail.html",
        Role.SELLER_MANUFACTURER: "dashboard/sellers/manufacturer.html",
        Role.SELLER_LOGISTICS: "dashboard/sellers/logistics.html",
        Role.SELLER_COMPONENT: "dashboard/sellers/component.html",
    }
    
    template_name = role_templates.get(role, template_name)

    return TemplateResponse(request, template_name, {
        "user": user,
        "form": form,
        "page_title": f"{user.get_role_display()} Dashboard"
    })

def seller_dashboard(request):
    return role_dashboard_router(request)

def seller_my_products(request):
    """Sotuvchining o'z mahsulotlari ro'yxati."""
    if not request.user.is_authenticated or not request.user.is_seller:
        return redirect("auth_login")

    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    
    # Audit: seller va is_active/is_featured maydonlari ishlatilmoqda
    products = Product.objects.filter(seller=request.user)
    
    if search_query:
        products = products.filter(
            Q(title_uz__icontains=search_query) | 
            Q(sku__icontains=search_query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    categories = Category.objects.filter(is_active=True, parent=None)

    context = {
        "products": products,
        "categories": categories,
        "search_query": search_query,
        "selected_category": category_id,
        "page_title": "Mening mahsulotlarim"
    }

    if request.headers.get("HX-Request") and not request.headers.get("HX-Target") == "modal-container":
        return TemplateResponse(request, "dashboard/sellers/partials/product_list_fragment.html", context)

    return TemplateResponse(request, "dashboard/sellers/my_products.html", context)

def toggle_product_status(request, product_id):
    """Mahsulot statusini o'zgartirish (HTMX)."""
    if not request.user.is_authenticated or not request.user.is_seller:
        return HttpResponseForbidden()

    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product.is_active = not product.is_active
    product.save()

    response = TemplateResponse(request, "dashboard/sellers/partials/product_card.html", {"product": product})
    response["HX-Trigger"] = '{"showToast": "Holat muvaffaqiyatli o\'zgartirildi!"}'
    return response

def update_product_price(request, product_id):
    """Mahsulot narxini inline yangilash (HTMX)."""
    if not request.user.is_authenticated or not request.user.is_seller:
        return HttpResponseForbidden()

    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == "POST":
        new_price = request.POST.get("price")
        if new_price:
            product.price = new_price
            product.save()
            response = TemplateResponse(request, "dashboard/sellers/partials/product_card.html", {"product": product})
            response["HX-Trigger"] = '{"showToast": "Narx yangilandi!"}'
            return response

    return TemplateResponse(request, "dashboard/sellers/partials/price_inline_form.html", {"product": product})

def add_product_modal(request):
    """Yangi mahsulot qo'shish modal oynasi."""
    if not request.user.is_authenticated or not request.user.is_seller:
        return HttpResponseForbidden()
    
    categories = Category.objects.filter(is_active=True)
    return TemplateResponse(request, "dashboard/sellers/partials/add_product_modal.html", {"categories": categories})
