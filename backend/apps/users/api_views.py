from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Role

class BaseRoleProfileView(APIView):
    """Base view for role-specific profile APIs."""
    permission_classes = [permissions.IsAuthenticated]
    required_role = None
    role_name = ""

    def check_permissions(self, request):
        super().check_permissions(request)
        if request.user.role != self.required_role and not request.user.is_superuser:
            self.permission_denied(
                request, 
                message=f"Ushbu API faqat '{self.role_name}' roli uchun ruxsat etilgan."
            )

    def get_dummy_data(self, request):
        return {}

    def get(self, request, *args, **kwargs):
        data = {
            "status": "success",
            "role": self.required_role,
            "role_display": self.role_name,
            "user": {
                "id": str(request.user.id),
                "username": request.user.username,
                "email": request.user.email,
            },
            "data": self.get_dummy_data(request)
        }
        return Response(data)

# 1. Partners
class PartnerMaterialView(BaseRoleProfileView):
    required_role = Role.PARTNER_MATERIAL
    role_name = "Xom-ashyo hamkori"
    
    def get_dummy_data(self, request):
        return {
            "contracts": [
                {"id": 101, "title": "Yog'och yetkazib berish shartnomasi", "status": "Active", "date": "2026-01-15"},
                {"id": 102, "title": "DSP panel lizingi", "status": "Pending", "date": "2026-02-10"},
                {"id": 103, "title": "Furnitura import kelishuvi", "status": "Completed", "date": "2025-12-05"},
                {"id": 104, "title": "Yelim materiallari shartnomasi", "status": "Active", "date": "2026-03-01"},
                {"id": 105, "title": "Laminat yetkazib berish", "status": "Active", "date": "2026-04-12"},
            ]
        }

class PartnerServiceView(BaseRoleProfileView):
    required_role = Role.PARTNER_SERVICE
    role_name = "Servis hamkori (Sug'urta/Kredit)"
    
    def get_dummy_data(self, request):
        return {
            "active_services": [
                {"id": 201, "name": "Kredit liniyasi #1", "clients": 45, "status": "Open"},
                {"id": 202, "name": "Sug'urta paketi 'Mebel-Safe'", "clients": 120, "status": "Active"},
                {"id": 203, "name": "Bo'lib to'lash xizmati", "clients": 89, "status": "Active"},
                {"id": 204, "name": "Logistika sug'urtasi", "clients": 12, "status": "Under Review"},
                {"id": 205, "name": "Biznes konsalting", "clients": 5, "status": "Maintenance"},
            ]
        }

# 2. Specialists
class DesignerInteriorView(BaseRoleProfileView):
    required_role = Role.DESIGNER_INTERIOR
    role_name = "Interyer dizayner"
    
    def get_dummy_data(self, request):
        return {
            "projects": [
                {"id": 301, "name": "Penthouse Tashkent City", "client": "Anvar T.", "stage": "Rendering"},
                {"id": 302, "name": "Office Loft", "client": "TechCorp", "stage": "Completed"},
                {"id": 303, "name": "Villa Samarkand", "client": "Private", "stage": "Moodboard"},
                {"id": 304, "name": "Cafe 'Retro'", "client": "Gourmet LLC", "stage": "Execution"},
                {"id": 305, "name": "Kitchen Design #45", "client": "Sevara O.", "stage": "Draft"},
            ]
        }

class Designer3DView(BaseRoleProfileView):
    required_role = Role.DESIGNER_3D
    role_name = "3D Dizayner"
    
    def get_dummy_data(self, request):
        return {
            "models": [
                {"id": 401, "name": "Modern Sofa V2", "poly_count": "450k", "status": "Ready"},
                {"id": 402, "name": "Classic Bed #09", "poly_count": "1.2M", "status": "In Progress"},
                {"id": 403, "name": "Office Chair Rigged", "poly_count": "200k", "status": "Ready"},
                {"id": 404, "name": "Kitchen Set Modular", "poly_count": "2.5M", "status": "Draft"},
                {"id": 405, "name": "Texture Pack: Wood", "poly_count": "N/A", "status": "Ready"},
            ]
        }

class FixerMasterView(BaseRoleProfileView):
    required_role = Role.FIXER_MASTER
    role_name = "O'rnatuvchi usta (Sborka)"
    
    def get_dummy_data(self, request):
        return {
            "assignments": [
                {"id": 501, "order": "ORD-778", "location": "Yunusobod", "date": "Today, 14:00"},
                {"id": 502, "order": "ORD-780", "location": "Chilonzor", "date": "Tomorrow, 09:00"},
                {"id": 503, "order": "ORD-785", "location": "Sergeli", "date": "Friday, 11:30"},
                {"id": 504, "order": "ORD-790", "location": "Mirobod", "date": "Pending"},
                {"id": 505, "order": "ORD-792", "location": "Mirzo Ulugbek", "date": "Completed"},
            ]
        }

class FixerRepairView(BaseRoleProfileView):
    required_role = Role.FIXER_REPAIR
    role_name = "Ta'mirlash ustasi"
    
    def get_dummy_data(self, request):
        return {
            "repair_tasks": [
                {"id": 601, "item": "Antikvar Stol", "issue": "Oyoq sinishi", "priority": "High"},
                {"id": 602, "item": "Charm Divan", "issue": "Qoplama almashtirish", "priority": "Medium"},
                {"id": 603, "item": "Oshxona shkafi", "issue": "Mexanizm nosozligi", "priority": "Low"},
                {"id": 604, "item": "Ofis kreslosi", "issue": "Pnevmatika", "priority": "Medium"},
                {"id": 605, "item": "Eski Komod", "issue": "Restavratsiya", "priority": "High"},
            ]
        }

# 3. Sellers
class SellerRetailView(BaseRoleProfileView):
    required_role = Role.SELLER_RETAIL
    role_name = "Chakana sotuvchi (Retail)"
    
    def get_dummy_data(self, request):
        return {
            "inventory": [
                {"id": 701, "name": "Yumshoq kreslo 'Comfort'", "stock": 15, "price": 1200000},
                {"id": 702, "name": "Yotoqxona to'plami 'Silk'", "stock": 4, "price": 8500000},
                {"id": 703, "name": "Mehmonxona stoli", "stock": 25, "price": 450000},
                {"id": 704, "name": "Bolalar kravati", "stock": 8, "price": 2100000},
                {"id": 705, "name": "Jurnal stoli", "stock": 40, "price": 300000},
            ]
        }

class SellerManufacturerView(BaseRoleProfileView):
    required_role = Role.SELLER_MANUFACTURER
    role_name = "Ishlab chiqaruvchi (Manufacturer)"
    
    def get_dummy_data(self, request):
        return {
            "production_line": [
                {"id": 801, "batch": "B-202", "product": "Shkaf-Kupe", "status": "Cutting"},
                {"id": 802, "batch": "B-203", "product": "Oshxona 'Elite'", "status": "Assembling"},
                {"id": 803, "batch": "B-204", "product": "Ofis stoli", "status": "Pending"},
                {"id": 804, "batch": "B-205", "product": "Eshiklar", "status": "Painting"},
                {"id": 805, "batch": "B-206", "product": "Krovat ramasi", "status": "Completed"},
            ]
        }

class SellerLogisticsView(BaseRoleProfileView):
    required_role = Role.SELLER_LOGISTICS
    role_name = "Logistika (Dostavka)"
    
    def get_dummy_data(self, request):
        return {
            "deliveries": [
                {"id": 901, "route": "Tashkent - Chirchiq", "vehicle": "Isuzu", "status": "On Route"},
                {"id": 902, "route": "Tashkent - Bukhara", "vehicle": "DAF", "status": "Loading"},
                {"id": 903, "route": "City Delivery #45", "vehicle": "Damas", "status": "Pending"},
                {"id": 904, "route": "Express #9", "vehicle": "Labo", "status": "Completed"},
                {"id": 905, "route": "International (Almaty)", "vehicle": "Volvo", "status": "Border Control"},
            ]
        }

class SellerComponentView(BaseRoleProfileView):
    required_role = Role.SELLER_COMPONENT
    role_name = "Furnitura va qismlar sotuvchisi"
    
    def get_dummy_data(self, request):
        return {
            "components": [
                {"id": 1001, "name": "Blum Petlya", "category": "Aksessuar", "qty": 1500},
                {"id": 1002, "name": "Alyumin profil", "category": "Profil", "qty": 800},
                {"id": 1003, "name": "Gidravlika", "category": "Mexanizm", "qty": 450},
                {"id": 1004, "name": "LDSP kronka", "category": "Dekor", "qty": 3000},
                {"id": 1005, "name": "Tutqich 'Modern'", "category": "Dekor", "qty": 1200},
            ]
        }
