from __future__ import annotations

from typing import Any

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_handoff_report,
    read_feature_metadata,
)
from .policy import WorkspacePolicy
from .status_workspace import _empty_feature_metadata
from .status_features_helpers import (
    _invalid_feature_summary,
    _missing_feature_summary,
)
from ._summary_policy import _evaluate_policy_coverage

__all__ = [
    "_build_single_feature_summary",
]


def _build_single_feature_summary(
    resolved_root: Any,
    feature: dict[str, object],
    *,
    require_coverage: bool,
    policy: WorkspacePolicy | None,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    status = str(feature.get("status") or "unknown")
    try:
        metadata = read_feature_metadata(resolved_root, slug)
    except InvalidFeatureSlug:
        metadata = _empty_feature_metadata()

    policy_coverage_required = _evaluate_policy_coverage(
        policy, slug, metadata, status,
    )
    summary_require_coverage = require_coverage or policy_coverage_required

    try:
        report = build_feature_handoff_report(
            resolved_root,
            slug,
            require_coverage=summary_require_coverage,
        )
    except InvalidFeatureSlug as error:
        return _invalid_feature_summary(
            feature,
            reason=str(error),
            require_coverage=summary_require_coverage,
            policy=policy,
            policy_coverage_required=policy_coverage_required,
        )
    except FeatureBundleNotFoundError:
        return _missing_feature_summary(
            feature,
            require_coverage=summary_require_coverage,
            policy=policy,
            policy_coverage_required=policy_coverage_required,
        )

    summary = report.summary
    feature_summary: dict[str, Any] = {
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
    return feature_summary
