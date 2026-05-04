"""
apps.management — Bittada ERP Boshqaruv Ekotizimi.

Maqsad: Django'ning standart admin panelidan to'liq mustaqil bo'lgan,
zamonaviy API va custom UI'ga ega bo'lgan boshqaruv tizimi.

Tarkib:
    - urls.py:       /dashboard/* HTML sahifa yo'llari (sidebar tugmalari)
    - api_urls.py:   /dashboard/api/v1/* DRF API yo'llari (AJAX/HTMX manbai)
    - views.py:      Django Template Views (HTML render)
    - api/viewsets.py: DRF ModelViewSet'lar (JSON API)
    - permissions.py: IsManagementUser - kim kira oladi
    - middleware.py:  ManagementAccessMiddleware - "Firewall"
    - selectors.py:   Faqat o'qish querylar (optimizatsiyalangan)
    - services.py:    Yozish operatsiyalari (transactional)

Foydalanuvchilar:
    - is_staff=True yoki is_superuser=True
    - Yoki Role IN (seller, admin, super_admin)
    - Boshqalar (customer va anonim) — /login/ ga yo'naltiriladi (Firewall)
"""
