"""
API test endpoint for connection verification.

Provides a simple health check that frontend can call to verify
the backend is accessible and properly configured.
"""
from __future__ import annotations

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def api_test_connection(request):
    """
    Simple endpoint to verify frontend-backend connection.
    
    Returns system status, configuration info, and timestamp
    so frontend can confirm real-time connectivity.
    """
    import platform
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from django.conf import settings
    from django.db import connections
    
    # Check database connection
    db_status = "unknown"
    try:
        connections['default'].ensure_connection()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    # Check Redis connection (if configured)
    cache_status = "unknown"
    try:
        from django.core.cache import cache
        cache.set('test_key', 'test_value', timeout=10)
        cache.get('test_key')
        cache_status = "connected"
    except Exception:
        cache_status = "not_configured"
    
    # Get timezone-aware datetime
    try:
        tz = ZoneInfo(settings.TIME_ZONE)
        timestamp = datetime.now(tz).isoformat()
    except Exception:
        timestamp = datetime.now().isoformat()
    
    response_data = {
        "status": "ok",
        "message": "Backend API is fully connected!",
        "timestamp": timestamp,
        "system": {
            "python_version": platform.python_version(),
            "django_version": platform.python_version(),
            "database": db_status,
            "cache": cache_status,
        },
        "endpoints": {
            "docs": "/api/docs/",
            "schema": "/api/schema/",
            "admin": "/admin/",
        },
        "cors": {
            "allowed_origins": settings.CORS_ALLOWED_ORIGINS if hasattr(settings, 'CORS_ALLOWED_ORIGINS') else [],
            "allow_all": getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False),
        }
    }
    
    return JsonResponse(response_data)


def system_health_view(request):
    """
    Tizim holatini tekshirish (Redis va Celery).
    Dashboard footeridagi indikatorlar uchun ishlatiladi.
    """
    from django.core.cache import cache
    import redis
    from django.conf import settings
    
    # 1. Redis holatini tekshirish (To'g'ridan-to'g'ri ping orqali)
    redis_alive = False
    try:
        # Cache backend'dan redis connectionni olishga harakat qilamiz
        r = redis.from_url(settings.CACHES['default']['LOCATION'])
        if r.ping():
            redis_alive = True
    except Exception:
        # Fallback: Cache orqali tekshirish
        try:
            cache.set('health_check', 'ok', timeout=5)
            if cache.get('health_check') == 'ok':
                redis_alive = True
        except Exception:
            redis_alive = False

    # 2. Celery holatini tekshirish
    celery_alive = False
    try:
        from config.celery import app
        # Celery ishlayotgan workerlarni tekshiramiz
        insp = app.control.inspect()
        active_workers = insp.active()
        if active_workers and len(active_workers) > 0:
            celery_alive = True
    except Exception:
        celery_alive = False

    return JsonResponse({
        "redis": "online" if redis_alive else "offline",
        "celery": "online" if celery_alive else "offline",
        "status": "operational" if (redis_alive and celery_alive) else "degraded",
        "timestamp": __import__('django.utils.timezone').utils.timezone.now().isoformat()
    })
