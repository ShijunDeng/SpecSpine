from __future__ import annotations

from typing import Any

from .status_workspace import (
    _FEATURE_SUMMARY_DEFAULT_VALUES,
    _FEATURE_SUMMARY_EFFORT_ORDER,
    _FEATURE_SUMMARY_PRIORITY_ORDER,
    _FEATURE_SUMMARY_STATUS_ORDER,
)
from .status_features_filters_matching import (
    _feature_summary_status_bucket,
    _feature_summary_tasks_open,
)

__all__ = [
    "_feature_summary_sort_value",
    "_feature_summary_sort_metadata_desc",
]


def _feature_summary_sort_value(summary: dict[str, Any], sort_key: str) -> tuple[Any, ...]:
    slug = str(summary.get("slug") or summary.get("feature_id") or "")
    if sort_key == "slug":
        return (slug,)
    if sort_key == "status":
        bucket = _feature_summary_status_bucket(summary)
        status = str(summary.get("status") or "unknown")
        return (_FEATURE_SUMMARY_STATUS_ORDER[bucket], status, slug)
    if sort_key == "ready":
        return (bool(summary.get("ready", False)), slug)
    if sort_key == "gaps":
        return (int(summary.get("gaps", 0)), slug)
    if sort_key == "blocking":
        return (int(summary.get("blocking_checks", 0)), slug)
    if sort_key == "tasks-open":
        return (_feature_summary_tasks_open(summary), slug)
    if sort_key == "priority":
        priority = str(summary.get("priority") or "unknown").lower()
        order = _FEATURE_SUMMARY_PRIORITY_ORDER.get(
            priority,
            _FEATURE_SUMMARY_PRIORITY_ORDER["unknown"],
        )
        return (order, slug)
    if sort_key in {"milestone", "target-release", "project"}:
        field = "target_release" if sort_key == "target-release" else sort_key
        default = _FEATURE_SUMMARY_DEFAULT_VALUES[sort_key]
        value = str(summary.get(field) or default).strip() or default
        default_bucket = 1 if value.lower() == default else 0
        return (default_bucket, value.lower(), value, slug)
    if sort_key == "effort":
        effort = str(summary.get("effort") or "unknown").strip() or "unknown"
        effort_key = effort.lower()
        order = _FEATURE_SUMMARY_EFFORT_ORDER.get(
            effort_key,
            _FEATURE_SUMMARY_EFFORT_ORDER["unknown"],
        )
        default_bucket = 1 if effort_key == "unknown" else 0
        return (default_bucket, order, effort_key, slug)
    return (slug,)


def _feature_summary_sort_metadata_desc(
    summaries: list[dict[str, Any]],
    sort_key: str,
) -> list[dict[str, Any]]:
    assigned: list[dict[str, Any]] = []
    defaults: list[dict[str, Any]] = []
    for summary in summaries:
        if _feature_summary_sort_value(summary, sort_key)[0] == 0:
            assigned.append(summary)
        else:
            defaults.append(summary)

    def slug_key(summary: dict[str, Any]) -> str:
        return str(summary.get("slug") or summary.get("feature_id") or "")

    assigned_by_slug = sorted(assigned, key=slug_key)
    return [
        *sorted(
            assigned_by_slug,
            key=lambda summary: _feature_summary_sort_value(summary, sort_key)[1:3],
            reverse=True,
        ),
        *sorted(defaults, key=slug_key),
    ]
