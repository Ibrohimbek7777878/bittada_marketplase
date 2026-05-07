#!/usr/bin/env python
"""Django CLI entrypoint."""
from __future__ import annotations

import os
import sys

# Ensure the project root (backend/) is on sys.path so that
# `apps.*`, `config.*`, and `core.*` are importable regardless
# of the working directory Django is started from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Django not installed or virtualenv not active. "
            "Install requirements first: pip install -r requirements/dev.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
