from __future__ import annotations

from pathlib import Path
from typing import Any

from .features import list_feature_bundles
from .policy import load_workspace_policy
from .status_features_filters import filter_and_sort_feature_summaries
from ._status_summary_builder import _build_single_feature_summary

__all__ = [
    "build_feature_summaries",
]


def build_feature_summaries(
    root: Path,
    features: list[dict[str, object]] | None = None,
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
    require_coverage: bool = False,
    use_policy: bool = False,
) -> list[dict[str, Any]]:
    resolved_root = root.expanduser().resolve()
    summaries: list[dict[str, Any]] = []
    feature_bundles = features if features is not None else list_feature_bundles(resolved_root)
    policy = load_workspace_policy(resolved_root) if use_policy else None

    for feature in feature_bundles:
        summary = _build_single_feature_summary(
            resolved_root,
            feature,
            require_coverage=require_coverage,
            policy=policy,
        )
        summaries.append(summary)

    return filter_and_sort_feature_summaries(
        summaries,
        status_filters=status_filters,
        ready_filter=ready_filter,
        priority_filters=priority_filters,
        owner_filters=owner_filters,
        milestone_filters=milestone_filters,
        target_release_filters=target_release_filters,
        project_filters=project_filters,
        effort_filters=effort_filters,
        sort_key=sort_key,
        sort_desc=sort_desc,
    )
