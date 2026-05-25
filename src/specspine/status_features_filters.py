from __future__ import annotations

from typing import Any

from .status_workspace import (
    FEATURE_SUMMARY_STATUS_FILTERS,
    _FEATURE_SUMMARY_DEFAULT_VALUES,
    _FEATURE_SUMMARY_EFFORT_ORDER,
    _FEATURE_SUMMARY_PRIORITY_ORDER,
    _FEATURE_SUMMARY_STATUS_ORDER,
)

__all__ = [
    "_feature_summary_status_bucket",
    "_feature_summary_matches_status",
    "_feature_summary_matches_priority",
    "_feature_summary_matches_owner",
    "_feature_summary_matches_metadata",
    "_feature_summary_tasks_open",
    "_feature_summary_sort_value",
    "_feature_summary_sort_metadata_desc",
    "filter_and_sort_feature_summaries",
]


def _feature_summary_status_bucket(summary: dict[str, Any]) -> str:
    status = str(summary.get("status") or "unknown")
    if status == "unknown":
        return "unknown"
    if status in FEATURE_SUMMARY_STATUS_FILTERS:
        return status
    return "invalid"


def _feature_summary_matches_status(
    summary: dict[str, Any],
    status_filters: tuple[str, ...],
) -> bool:
    if not status_filters:
        return True

    status = str(summary.get("status") or "unknown")
    status_bucket = _feature_summary_status_bucket(summary)
    return status in status_filters or status_bucket in status_filters


def _feature_summary_matches_priority(
    summary: dict[str, Any],
    priority_filters: tuple[str, ...],
) -> bool:
    if not priority_filters:
        return True

    priority = str(summary.get("priority") or "unknown").lower()
    return priority in priority_filters


def _feature_summary_matches_owner(
    summary: dict[str, Any],
    owner_filters: tuple[str, ...],
) -> bool:
    if not owner_filters:
        return True

    owner = str(summary.get("owner") or "unassigned").strip().lower() or "unassigned"
    return owner in owner_filters


def _feature_summary_matches_metadata(
    summary: dict[str, Any],
    field: str,
    filters: tuple[str, ...],
    *,
    default: str,
) -> bool:
    if not filters:
        return True

    value = str(summary.get(field) or default).strip().lower() or default
    return value in filters


def _feature_summary_tasks_open(summary: dict[str, Any]) -> int:
    tasks = summary.get("tasks_summary", {})
    if not isinstance(tasks, dict):
        return 0
    value = tasks.get("open", 0)
    return int(value) if isinstance(value, int) else 0


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


def filter_and_sort_feature_summaries(
    summaries: list[dict[str, Any]],
    *,
    status_filters: tuple[str, ...] = (),
    ready_filter: bool | None = None,
    priority_filters: tuple[str, ...] = (),
    owner_filters: tuple[str, ...] = (),
    milestone_filters: tuple[str, ...] = (),
    target_release_filters: tuple[str, ...] = (),
    project_filters: tuple[str, ...] = (),
    effort_filters: tuple[str, ...] = (),
    sort_key: str | None = None,
    sort_desc: bool = False,
) -> list[dict[str, Any]]:
    filtered = [
        summary
        for summary in summaries
        if _feature_summary_matches_status(summary, status_filters)
        and _feature_summary_matches_priority(summary, priority_filters)
        and _feature_summary_matches_owner(summary, owner_filters)
        and _feature_summary_matches_metadata(
            summary,
            "milestone",
            milestone_filters,
            default="unassigned",
        )
        and _feature_summary_matches_metadata(
            summary,
            "target_release",
            target_release_filters,
            default="unassigned",
        )
        and _feature_summary_matches_metadata(
            summary,
            "project",
            project_filters,
            default="unassigned",
        )
        and _feature_summary_matches_metadata(
            summary,
            "effort",
            effort_filters,
            default="unknown",
        )
        and (
            ready_filter is None
            or bool(summary.get("ready", False)) is ready_filter
        )
    ]

    if sort_key is not None:
        if sort_desc and sort_key in _FEATURE_SUMMARY_DEFAULT_VALUES:
            return _feature_summary_sort_metadata_desc(filtered, sort_key)
        return sorted(
            filtered,
            key=lambda summary: _feature_summary_sort_value(summary, sort_key),
            reverse=sort_desc,
        )

    if sort_desc:
        filtered.reverse()

    return filtered
