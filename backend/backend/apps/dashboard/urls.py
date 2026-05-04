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
    
    # Management
    path('management/users/', views.user_management, name='user_management'),
    path('management/blacklist/', views.blacklist_logic, name='blacklist_logic'),
    
    # System & Operations
    path('system/health/', views.system_health_logs, name='system_health_logs'),
    path('operations/pending/', views.pending_actions, name='pending_actions'),
]
