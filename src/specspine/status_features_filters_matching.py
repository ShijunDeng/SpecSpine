from __future__ import annotations

from typing import Any

from .status_workspace import (
    FEATURE_SUMMARY_STATUS_FILTERS,
)

__all__ = [
    "_feature_summary_status_bucket",
    "_feature_summary_matches_status",
    "_feature_summary_matches_priority",
    "_feature_summary_matches_owner",
    "_feature_summary_matches_metadata",
    "_feature_summary_tasks_open",
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
