from __future__ import annotations

__all__ = [
    "_summary",
]


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


def _count_by(features: list[dict[str, object]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for feature in features:
        value = str(feature[key])
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))
