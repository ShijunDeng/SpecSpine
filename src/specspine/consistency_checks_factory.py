from __future__ import annotations

from .consistency_models import ConsistencyCheck

__all__ = [
    "_check",
]


def _check(
    check_id: str,
    status: str,
    message: str,
) -> ConsistencyCheck:
    return ConsistencyCheck(id=check_id, status=status, message=message)
