from __future__ import annotations

from typing import Any

from .status_features_filters_matching import (
    _feature_summary_matches_status,
    _feature_summary_matches_priority,
    _feature_summary_matches_owner,
    _feature_summary_matches_metadata,
)
from .status_features_filters_sorting import (
    _feature_summary_sort_value,
    _feature_summary_sort_metadata_desc,
    _FEATURE_SUMMARY_DEFAULT_VALUES,
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

from .status_features_filters_matching import (
    _feature_summary_status_bucket,
    _feature_summary_tasks_open,
)


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
