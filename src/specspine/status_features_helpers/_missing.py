from __future__ import annotations

from typing import Any

from ..policy import WorkspacePolicy
from ..status_workspace import (
    _empty_count_summary,
    _empty_feature_metadata,
)

__all__ = [
    "_missing_feature_summary",
]


def _missing_feature_summary(
    feature: dict[str, object],
    *,
    require_coverage: bool = False,
    policy: WorkspacePolicy | None = None,
    policy_coverage_required: bool = False,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    missing_files = [
        str(relative_path)
        for relative_path in feature.get("missing_files", [])
    ]
    summary = {
        "feature_id": slug,
        "slug": slug,
        "status": str(feature.get("status") or "unknown"),
        **_empty_feature_metadata().as_dict(),
        "complete": bool(feature.get("complete", False)),
        "ready": False,
        "missing_files": missing_files,
        "tasks_summary": _empty_count_summary(),
        "ready_summary": {"fail": 1, "pass": 0, "total": 1},
        "gaps": max(1, len(missing_files)),
        "blocking_checks": 1,
        "next_actions": [
            (
                "Create or restore the native feature bundle: "
                f"specspine feature new {slug} . --title \"...\" --why \"...\""
            )
        ],
        "recommended_commands": [],
    }
    if require_coverage:
        summary["coverage_required"] = True
    if policy is not None:
        summary["policy_coverage_required"] = policy_coverage_required
        summary["policy_source"] = str(policy.source_file)
    return summary
