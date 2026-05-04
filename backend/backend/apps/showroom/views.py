"""Views for the `showroom` app — Django Templates."""
from __future__ import annotations

from django.template.response import TemplateResponse

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
