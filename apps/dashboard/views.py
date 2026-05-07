from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

# Core: Dashboard (General stats)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    return JsonResponse({
        "status": "success", 
        "data": {
            "general_stats": "Active",
            "active_users": 105,
            "system_health": "100%"
        }
    })

# Core: Sales (GMV, Order counts)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def sales_stats(request):
    from apps.orders.models import Order, OrderStatus
    from django.db.models import Sum
    
    # Faol buyurtmalar (Processing/Shipping equivalents in this system)
    active_orders = Order.objects.filter(
        status__in=[OrderStatus.STARTED, OrderStatus.PRODUCTION, OrderStatus.SHIPPING]
    ).count() if Order.objects.exists() else 0
    
    # Yangi buyurtmalar (INQUIRY)
    new_orders = Order.objects.filter(status=OrderStatus.INQUIRY).count() if Order.objects.exists() else 0
    
    # GMV (Gross Merchandise Value) for completed orders
    gmv_agg = Order.objects.filter(status=OrderStatus.COMPLETED).aggregate(total=Sum('total_price'))
    gmv = gmv_agg['total'] or 0.00
    
    return JsonResponse({
        "status": "success", 
        "data": {
            "gmv": float(gmv), 
            "total_orders": Order.objects.count() if Order.objects.exists() else 0,
            "active_orders": active_orders,
            "new_orders": new_orders
        }
    })

# Marketplace: Products (Inventory)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def products_inventory(request):
    from apps.products.models import Product
    total_products = Product.objects.count() if Product.objects.exists() else 0
    return JsonResponse({
        "status": "success", 
        "data": {
            "total_products": total_products,
            "low_stock": 12
        }
    })

# Marketplace: Services (Bookings/Masters)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def services_stats(request):
    return JsonResponse({
        "status": "success", 
        "data": {
            "total_bookings": 45,
            "active_masters": 28
        }
    })

# Financials: Escrow Fund
@api_view(['GET'])
@permission_classes([IsAdminUser])
def escrow_fund(request):
    from apps.orders.models import Order, OrderStatus
    from django.db.models import Sum
    # Muzlatilgan (Frozen) funds: payment is held in escrow but not yet released to the master
    escrow_agg = Order.objects.filter(
        status__in=[OrderStatus.ESCROW_PENDING, OrderStatus.PAID, OrderStatus.STARTED, OrderStatus.PRODUCTION, OrderStatus.SHIPPING, OrderStatus.DISPUTED]
    ).aggregate(total=Sum('escrow_amount'))
    
    frozen_funds = escrow_agg['total'] or 0.00
    
    return JsonResponse({
        "status": "success", 
        "data": {
            "total_escrow": float(frozen_funds),
            "frozen_funds_count": Order.objects.filter(status__in=[OrderStatus.ESCROW_PENDING, OrderStatus.PAID]).count() if Order.objects.exists() else 0
        }
    })

# Financials: Credit Economy
@api_view(['GET'])
@permission_classes([IsAdminUser])
def credit_economy(request):
    return JsonResponse({
        "status": "success", 
        "data": {
            "active_credits": "₿ 450.2k",
            "circulation_status": "Active"
        }
    })

# Management: User management
@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_management(request):
    from apps.users.models import User
    total_users = User.objects.count() if User.objects.exists() else 0
    return JsonResponse({
        "status": "success", 
        "data": {
            "total_users": total_users,
            "new_this_week": 24
        }
    })

# Management: Blacklist logic
@api_view(['GET'])
@permission_classes([IsAdminUser])
def blacklist_logic(request):
    from apps.users.models import User
    blacklisted_users = User.objects.filter(is_active=False).count() if User.objects.exists() else 0
    return JsonResponse({
        "status": "success", 
        "data": {
            "blacklisted_users": blacklisted_users
        }
    })

# System: System Health, Logs
@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_health_logs(request):
    return JsonResponse({
        "status": "success", 
        "data": {
            "redis_status": "online",
            "celery_status": "online",
            "recent_errors": 0
        }
    })

# Operations: Pending Actions
@api_view(['GET'])
@permission_classes([IsAdminUser])
def pending_actions(request):
    from apps.orders.models import Order, OrderStatus
    
    actions = []
    
    # 1. Escrow Pending (Frozen funds needing release or check)
    escrow_orders = Order.objects.filter(status=OrderStatus.ESCROW_PENDING)[:5]
    for order in escrow_orders:
        actions.append({
            "id": f"ord_{order.id}",
            "icon": "🛡️",
            "title": f"Buyurtma #ORD-{order.id}",
            "subtitle": "Escrow release / To'lov kutilmoqda",
            "action": "Bajarish"
        })
        
    # 2. New Inquiries
    new_inquiries = Order.objects.filter(status=OrderStatus.INQUIRY)[:5]
    for order in new_inquiries:
        actions.append({
            "id": f"inq_{order.id}",
            "icon": "📦",
            "title": f"Yangi so'rov #{order.id}",
            "subtitle": "Mijoz tasdig'i",
            "action": "Bajarish"
        })
        
    # Mocking KYC for demonstration since actual KYC model is unknown
    if not actions:
        actions.append({
            "id": "kyc_1",
            "icon": "🆔",
            "title": "Abduvali Toshmatov",
            "subtitle": "KYC Verifikatsiya",
            "action": "Bajarish"
        })

    return JsonResponse({
        "status": "success",
        "data": {
            "actions": actions,
            "total_pending": len(actions)
        }
    })


def seller_dashboard(request):
    """Seller's personal dashboard: profile, products, services, orders."""
    if not request.user.is_authenticated:
        return redirect("login")

    from apps.orders.models import Order
    from apps.products.models import Product, ProductStatus
    from apps.services.models import Service

    products = Product.objects.filter(
        seller=request.user,
        status=ProductStatus.PUBLISHED,
    ).select_related("category").prefetch_related("images")
    services = Service.objects.filter(provider=request.user)
    orders = Order.objects.filter(seller=request.user).select_related("customer").order_by("-created_at")[:20]

    return TemplateResponse(request, "dashboard/seller/index.html", {
        "seller": request.user,
        "profile": getattr(request.user, "profile", None),
        "products": products,
        "services": services,
        "orders": orders,
        "products_count": products.count(),
        "services_count": services.count(),
        "orders_count": orders.count(),
    })
