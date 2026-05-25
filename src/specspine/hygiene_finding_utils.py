from __future__ import annotations

from .hygiene_models import (
    HygieneFinding,
)

__all__ = [
    "_add_finding",
]


def _add_finding(
    findings: list[HygieneFinding],
    *,
    finding_id: str,
    severity: str,
    category: str,
    path: str,
    message: str,
    source: str,
    line: int | None = None,
) -> None:
    findings.append(
        HygieneFinding(
            id=finding_id,
            severity=severity,
            category=category,
            path=path,
            line=line,
            message=message,
            source=source,
        )
    )
