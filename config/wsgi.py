"""WSGI entrypoint (sync, used by gunicorn for HTTP)."""
from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

# Use development settings by default for local development
# Production deployments should set DJANGO_SETTINGS_MODULE environment variable
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
else:
    # If DJANGO_SETTINGS_MODULE is explicitly set, use it
    pass

application = get_wsgi_application()
