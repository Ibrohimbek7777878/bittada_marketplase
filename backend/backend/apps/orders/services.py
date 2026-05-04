"""
Business logic for `orders`.

Functions in this module mutate state. They should:
- accept primitive args + the actor user;
- run inside a transaction when touching multiple rows;
- raise `core.exceptions.DomainError` on rule violations;
- emit notifications/Celery tasks rather than inline I/O.
"""
from __future__ import annotations
