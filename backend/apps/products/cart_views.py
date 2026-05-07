from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(["GET"])
def api_cart_count(request):
    """Savatchadagi mahsulotlar sonini qaytarish (Placeholder)."""
    return JsonResponse({"count": 0})
