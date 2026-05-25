from __future__ import annotations

__all__ = [
    "_count_by",
    "_themes",
]


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


def _count_by(features: list[dict[str, object]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for feature in features:
        value = str(feature[key])
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))
