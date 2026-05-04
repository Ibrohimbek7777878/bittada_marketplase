"""
Read queries for `i18n_extra`.

Pure functions returning querysets / dicts. No side effects, no writes.
Optimize with `select_related` / `prefetch_related` here, not in views.
"""
from __future__ import annotations
