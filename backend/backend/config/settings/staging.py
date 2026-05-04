"""Staging — production-like, with verbose logging and a separate DB."""
from __future__ import annotations

from .prod import *  # noqa: F401, F403

DEBUG = False
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
