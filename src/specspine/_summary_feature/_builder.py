from __future__ import annotations

from typing import Any

from ..features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_handoff_report,
)
from ..policy import WorkspacePolicy
from ..status_features_helpers import (
    _invalid_feature_summary,
    _missing_feature_summary,
)
from ._context import _resolve_feature_context

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
    context = _resolve_feature_context(
        resolved_root,
        feature,
        require_coverage=require_coverage,
        policy=policy,
    )

    try:
        report = build_feature_handoff_report(
            resolved_root,
            context["slug"],
            require_coverage=context["summary_require_coverage"],
        )
    except InvalidFeatureSlug as error:
        return _invalid_feature_summary(
            feature,
            reason=str(error),
            require_coverage=context["summary_require_coverage"],
            policy=policy,
            policy_coverage_required=context["policy_coverage_required"],
        )
    except FeatureBundleNotFoundError:
        return _missing_feature_summary(
            feature,
            require_coverage=context["summary_require_coverage"],
            policy=policy,
            policy_coverage_required=context["policy_coverage_required"],
        )

    summary = report.summary
    metadata = context["metadata"]
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
    if context["summary_require_coverage"]:
        feature_summary["coverage_required"] = True
    if policy is not None:
        feature_summary["policy_coverage_required"] = context["policy_coverage_required"]
        feature_summary["policy_source"] = str(policy.source_file)
    return feature_summary
