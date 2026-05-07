from django.urls import path
from .api_views import (
    PartnerMaterialView, PartnerServiceView,
    DesignerInteriorView, Designer3DView,
    FixerMasterView, FixerRepairView,
    SellerRetailView, SellerManufacturerView,
    SellerLogisticsView, SellerComponentView
)

urlpatterns = [
    # 1. Partners
    path("partner-material/", PartnerMaterialView.as_view(), name="api_partner_material"),
    path("partner-service/", PartnerServiceView.as_view(), name="api_partner_service"),
    
    # 2. Specialists
    path("designer-interior/", DesignerInteriorView.as_view(), name="api_designer_interior"),
    path("designer-3d/", Designer3DView.as_view(), name="api_designer_3d"),
    path("fixer-master/", FixerMasterView.as_view(), name="api_fixer_master"),
    path("fixer-repair/", FixerRepairView.as_view(), name="api_fixer_repair"),
    
    # 3. Sellers
    path("seller-retail/", SellerRetailView.as_view(), name="api_seller_retail"),
    path("seller-manufacturer/", SellerManufacturerView.as_view(), name="api_seller_manufacturer"),
    path("seller-logistics/", SellerLogisticsView.as_view(), name="api_seller_logistics"),
    path("seller-component/", SellerComponentView.as_view(), name="api_seller_component"),
]
