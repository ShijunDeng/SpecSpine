from __future__ import annotations


def _recommendation_sort_key(feature: dict[str, object]) -> tuple[object, ...]:
    status = str(feature["status"])
    coverage = feature["coverage_state"]  # type: ignore[assignment]
    coverage_state = str(coverage["state"])  # type: ignore[index]
    task_counts = feature["task_counts"]  # type: ignore[assignment]
    return (
        bool(feature["ready"]),
        -len(feature["blocking_checks"]),  # type: ignore[arg-type]
        -int(feature["gap_count"]),
        -int(task_counts["open"]),  # type: ignore[index]
        0 if coverage_state in {"missing", "partial"} else 1,
        0 if status not in {"implemented", "validated", "archived"} else 1,
        str(feature["feature_id"]),
    )


def _recommendation_reason(feature: dict[str, object]) -> str:
    if not feature["ready"]:
        checks = feature["blocking_checks"]  # type: ignore[assignment]
        if checks:
            first = checks[0]  # type: ignore[index]
            return f"Not ready: {first['id']}."
        return "Not ready."
    coverage = feature["coverage_state"]  # type: ignore[assignment]
    if coverage["state"] in {"missing", "partial"}:  # type: ignore[index]
        return f"Coverage is {coverage['state']}."  # type: ignore[index]
    return "Ready feature included for trend review."


def _build_recommendations(
    features: list[dict[str, object]],
    *,
    limit: int | None,
) -> list[dict[str, object]]:
    ranked = sorted(features, key=_recommendation_sort_key)
    rows = [
        {
            "feature_id": feature["feature_id"],
            "rank": index,
            "reason": _recommendation_reason(feature),
            "recommended_commands": feature["recommended_commands"],
            "status": feature["status"],
        }
        for index, feature in enumerate(ranked, start=1)
    ]
    if limit is not None:
        return rows[:limit]
    return rows


__all__ = [
    "_build_recommendations",
    "_recommendation_reason",
    "_recommendation_sort_key",
]
