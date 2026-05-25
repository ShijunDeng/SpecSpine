from __future__ import annotations

from pathlib import Path

from ..features import (
    FEATURE_STATUSES,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)

from .retrospective_constants import SAFETY_NOTES
from .retrospective_commands import _recommended_feature_commands, _workspace_commands
from .retrospective_records import _coverage_state, _count_by, _feature_record

__all__ = [
    "_coverage_state",
    "_count_by",
    "_empty_report",
    "_feature_record",
    "_summary",
    "_themes",
    "_workspace_commands",
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
        "safety_notes": list(SAFETY_NOTES),
        "summary": _summary([], missing_feature=missing_feature),
        "themes": _themes([]),
    }


def _summary(
    features: list[dict[str, object]],
    *,
    missing_feature: str | None,
) -> dict[str, object]:
    total = len(features)
    ready = sum(1 for feature in features if bool(feature["ready"]))
    open_tasks = sum(
        int(feature["task_counts"]["open"])
        for feature in features
    )
    blocking_checks = sum(
        len(feature["blocking_checks"])
        for feature in features
    )
    gaps = sum(int(feature["gap_count"]) for feature in features)
    missing_coverage = sum(
        1
        for feature in features
        if feature["coverage_state"]["state"] in {"missing", "partial"}
    )
    return {
        "blocking_checks": blocking_checks,
        "features_missing_coverage": missing_coverage,
        "features_not_ready": total - ready,
        "features_ready": ready,
        "features_total": total,
        "gap_count": gaps,
        "missing_feature": missing_feature,
        "open_tasks": open_tasks,
        "recommendable_features": total,
        "statuses": _count_by(features, "status"),
    }


def _themes(features: list[dict[str, object]]) -> dict[str, object]:
    blockers: dict[str, int] = {}
    gaps: dict[str, int] = {}
    coverage: dict[str, int] = {}
    release_readiness_issues = 0
    features_with_open_tasks = 0
    open_tasks_total = 0

    for feature in features:
        task_counts = feature["task_counts"]
        open_tasks = int(task_counts["open"])
        if open_tasks:
            features_with_open_tasks += 1
            open_tasks_total += open_tasks

        coverage_state = str(feature["coverage_state"]["state"])
        coverage[coverage_state] = coverage.get(coverage_state, 0) + 1

        for check in feature["blocking_checks"]:
            check_id = str(check["id"])
            blockers[check_id] = blockers.get(check_id, 0) + 1
            if check_id == "feature.release_readiness":
                release_readiness_issues += 1

        for gap in feature["gaps"]:
            gap_id = str(gap["id"])
            gaps[gap_id] = gaps.get(gap_id, 0) + 1

    return {
        "blocking_checks": dict(sorted(blockers.items())),
        "coverage_states": dict(sorted(coverage.items())),
        "gaps": dict(sorted(gaps.items())),
        "open_tasks": {
            "features": features_with_open_tasks,
            "total": open_tasks_total,
        },
        "release_readiness_issues": release_readiness_issues,
        "statuses": _count_by(features, "status"),
    }
