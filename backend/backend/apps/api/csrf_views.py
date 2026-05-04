"""
CSRF token endpoint for SPA frontend.

Provides a dedicated endpoint to obtain CSRF cookie.
This is needed because DRF API endpoints don't set CSRF cookies automatically.
"""
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET


@require_GET
def get_csrf_token(request):
    """
    Return a CSRF token for SPA frontend.
    
    This endpoint ensures the CSRF cookie is set in the browser,
    which the frontend can then read and include in subsequent requests.
    
    Usage:
        GET /api/csrf-token/
        Response: {"csrfToken": "..."}
        Sets: csrftoken cookie
    """
    # This ensures the CSRF cookie is set in the response
    csrf_token = get_token(request)
    
    return JsonResponse({
        'csrfToken': csrf_token,
        'message': 'CSRF token cookie has been set'
    })
