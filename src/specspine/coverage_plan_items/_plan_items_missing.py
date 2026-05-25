from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import FEATURE_FILE_PATHS

from ._plan_items_helpers import _coverage_plan_safety_notes

__all__ = [
    "_missing_feature_plan_report",
]


def _missing_feature_plan_report(
    root: Path,
    *,
    feature_filter: str,
    use_policy: bool,
) -> dict[str, Any]:
    resolved_root = root.expanduser().resolve()
    missing_files = [
        relative_path.format(slug=feature_filter)
        for relative_path in FEATURE_FILE_PATHS.values()
    ]
    return {
        "error": "feature_not_found",
        "feature_filter": feature_filter,
        "items": [],
        "mode": "policy" if use_policy else "universal",
        "recommended_commands": [
            f"specspine feature new {feature_filter} .",
            "specspine coverage plan . --json",
        ],
        "root": str(resolved_root),
        "safety_notes": _coverage_plan_safety_notes(),
        "summary": {
            "acceptance_criteria_total": 0,
            "coverage_required_total": 0,
            "feature_missing": True,
            "features_scanned": 0,
            "features_with_plan_items": 0,
            "items_returned": 0,
            "items_total": 0,
            "missing_acceptance_criteria": 0,
            "missing_files": missing_files,
        },
    }
