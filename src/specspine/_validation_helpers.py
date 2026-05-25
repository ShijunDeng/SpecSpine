from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .validation_models import ValidationCheck, VALIDATION_STATUSES


def _check(
    check_id: str,
    status: str,
    message: str,
    *,
    severity: str | None = None,
) -> ValidationCheck:
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


def _relative_paths(paths: Iterable[Path], root: Path) -> set[str]:
    return {str(path.relative_to(root)) for path in paths}


__all__ = [
    "_check",
    "_relative_paths",
]
