from __future__ import annotations

from typing import Any

from .status_features_filters_matching import (
    _feature_summary_matches_status,
    _feature_summary_matches_priority,
    _feature_summary_matches_owner,
    _feature_summary_matches_metadata,
)

__all__ = [
    "_apply_feature_summary_filters",
]


def _apply_feature_summary_filters(
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
) -> list[dict[str, Any]]:
    return [
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
