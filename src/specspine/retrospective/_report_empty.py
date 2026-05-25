from __future__ import annotations

from pathlib import Path

from .retrospective_commands import _recommended_feature_commands, _workspace_commands
from ._summary_calc import _summary
from ._report_constants import _SAFETY_NOTES
from ._report_themes import _themes

__all__ = [
    "_empty_report",
]


def _empty_report(
    root: Path,
    *,
    feature_filter: str | None,
    missing_feature: str | None = None,
    limit: int | None = None,
) -> dict[str, object]:
    return {
        "features": [],
        "feature_filter": feature_filter,
        "recommendations": [],
        "recommended_commands": _workspace_commands(feature_filter),
        "root": str(root),
        "safety_notes": list(_SAFETY_NOTES),
        "summary": _summary([], missing_feature=missing_feature),
        "themes": _themes([]),
    }
