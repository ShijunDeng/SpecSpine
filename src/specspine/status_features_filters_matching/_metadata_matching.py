from __future__ import annotations

from typing import Any

__all__ = [
    "_feature_summary_matches_priority",
    "_feature_summary_matches_owner",
    "_feature_summary_matches_metadata",
]


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
