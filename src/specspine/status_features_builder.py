from __future__ import annotations

from pathlib import Path
from typing import Any

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_handoff_report,
    list_feature_bundles,
    read_feature_metadata,
)
from .policy import WorkspacePolicy, load_workspace_policy
from .status_workspace import _empty_feature_metadata
from .status_features_filters import filter_and_sort_feature_summaries
from .status_features_helpers import (
    _invalid_feature_summary,
    _missing_feature_summary,
)

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
        slug = str(feature["slug"])
        status = str(feature.get("status") or "unknown")
        try:
            metadata = read_feature_metadata(resolved_root, slug)
        except InvalidFeatureSlug:
            metadata = _empty_feature_metadata()
        policy_coverage_required = False
        if policy is not None:
            policy_coverage_required = policy.require_coverage.requires_coverage(
                feature_id=slug,
                metadata=metadata,
                status=status,
            )
        summary_require_coverage = require_coverage or policy_coverage_required
        try:
            report = build_feature_handoff_report(
                resolved_root,
                slug,
                require_coverage=summary_require_coverage,
            )
        except InvalidFeatureSlug as error:
            summaries.append(
                _invalid_feature_summary(
                    feature,
                    reason=str(error),
                    require_coverage=summary_require_coverage,
                    policy=policy,
                    policy_coverage_required=policy_coverage_required,
                )
            )
            continue
        except FeatureBundleNotFoundError:
            summaries.append(
                _missing_feature_summary(
                    feature,
                    require_coverage=summary_require_coverage,
                    policy=policy,
                    policy_coverage_required=policy_coverage_required,
                )
            )
            continue

        summary = report.summary
        feature_summary = {
            "feature_id": report.feature_id,
            "slug": report.feature_id,
            "status": report.status,
            **metadata.as_dict(),
            "complete": bool(feature.get("complete", False)),
            "ready": report.ready,
            "missing_files": list(report.missing_files),
            "tasks_summary": dict(summary["tasks"]),
            "ready_summary": dict(summary["ready"]),
            "gaps": int(summary["gaps"]["total"]),
            "blocking_checks": int(summary["blocking_checks"]["total"]),
            "next_actions": list(report.next_actions),
            "recommended_commands": list(report.recommended_commands),
        }
        if summary_require_coverage:
            feature_summary["coverage_required"] = True
        if policy is not None:
            feature_summary["policy_coverage_required"] = policy_coverage_required
            feature_summary["policy_source"] = str(policy.source_file)
        summaries.append(feature_summary)

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
