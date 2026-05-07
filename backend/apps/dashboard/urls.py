from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Core
    path('stats/general/', views.dashboard_stats, name='dashboard_stats'),
    path('stats/sales/', views.sales_stats, name='sales_stats'),
    
    # Marketplace
    path('inventory/products/', views.products_inventory, name='products_inventory'),
    path('inventory/services/', views.services_stats, name='services_stats'),
    
    # Financials
    path('financials/escrow/', views.escrow_fund, name='escrow_fund'),
    path('financials/credit-economy/', views.credit_economy, name='credit_economy'),

    # Seller Dashboard (Interactive)
    path('my-products/', views.seller_my_products, name='seller_my_products'),
    path('my-products/toggle/<uuid:product_id>/', views.toggle_product_status, name='toggle_product_status'),
    path('my-products/update-price/<uuid:product_id>/', views.update_product_price, name='update_product_price'),
    path('my-products/add-modal/', views.add_product_modal, name='add_product_modal'),
]
