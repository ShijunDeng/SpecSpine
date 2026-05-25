from __future__ import annotations

from pathlib import Path
from typing import Any

from .validation_models import ValidationCheck


def _check(
    check_id: str,
    status: str,
    message: str,
    *,
    severity: str | None = None,
) -> ValidationCheck:
    from .validation_models import VALIDATION_STATUSES
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


def _read_top_level_scalars(path: Path) -> dict[str, Any]:
    from .status import _clean_scalar
    if not path.exists():
        return {}

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    values: dict[str, Any] = {}
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent != 0 or ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        value = value.strip()
        if value:
            values[key.strip()] = _clean_scalar(value)

    return values


__all__ = [
    "_check",
    "_read_top_level_scalars",
]
