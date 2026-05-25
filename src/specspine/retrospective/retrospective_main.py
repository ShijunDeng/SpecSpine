from __future__ import annotations

from pathlib import Path

from .retrospective_validation import _validate_retrospective_input
from .retrospective_assembly import _assemble_retrospective_report, retrospective_report_exit_code

__all__ = [
    "build_retrospective_report",
    "retrospective_report_exit_code",
]


def build_retrospective_report(
    root: Path,
    *,
    feature_slug: str | None = None,
    limit: int | None = None,
) -> dict[str, object]:
    resolved_root, validated_slug = _validate_retrospective_input(
        root,
        feature_slug=feature_slug,
        limit=limit,
    )
    return _assemble_retrospective_report(
        resolved_root,
        feature_slug=validated_slug,
        limit=limit,
    )
