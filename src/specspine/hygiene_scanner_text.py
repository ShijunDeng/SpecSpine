from __future__ import annotations

from .hygiene_models import (
    HygieneFinding,
)
from .hygiene_scanner_utils import (
    _add_finding,
)

__all__ = [
    "_scan_text_file",
]


def _scan_text_file(
    findings: list[HygieneFinding],
    *,
    relative_path: str,
    text: str,
    patterns: tuple[str, ...],
) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern in patterns:
            if pattern not in line:
                continue
            _add_finding(
                findings,
                finding_id="forbidden-content-pattern",
                severity="high",
                category="forbidden_content",
                path=relative_path,
                line=line_number,
                message="Forbidden content pattern detected.",
                source=pattern,
            )
