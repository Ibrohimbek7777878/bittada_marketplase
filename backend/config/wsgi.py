"""WSGI entrypoint (sync, used by gunicorn for HTTP)."""
from __future__ import annotations

import os
import sys

# Ensure the project root (backend/) is on sys.path so that
# `apps.*`, `config.*`, and `core.*` are importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
application = get_wsgi_application()
