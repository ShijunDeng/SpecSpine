from __future__ import annotations

from ..validation_models import ValidationCheck


def _check(
    check_id: str,
    status: str,
    message: str,
    *,
    severity: str | None = None,
) -> ValidationCheck:
    from ..validation_models import VALIDATION_STATUSES
    if status not in VALIDATION_STATUSES:
        raise ValueError(f"Unsupported validation status: {status}")

    if severity is None:
        severity = {
            "fail": "error",
            "warn": "warning",
            "pass": "info",
            "skip": "info",
        }[status]

    return ValidationCheck(
        id=check_id,
        status=status,
        message=message,
        severity=severity,
    )


__all__ = [
    "_check",
]
