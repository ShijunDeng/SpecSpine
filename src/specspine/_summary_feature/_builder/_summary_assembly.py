from __future__ import annotations

from typing import Any

from ...features import FeatureBundleNotFoundError, InvalidFeatureSlug
from ...policy import WorkspacePolicy

__all__ = [
    "_assemble_feature_summary",
]


def _assemble_feature_summary(
    report: Any,
    metadata: Any,
    feature: dict[str, object],
    context: dict[str, Any],
    policy: WorkspacePolicy | None,
) -> dict[str, Any]:
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
    if context["summary_require_coverage"]:
        feature_summary["coverage_required"] = True
    if policy is not None:
        feature_summary["policy_coverage_required"] = context["policy_coverage_required"]
        feature_summary["policy_source"] = str(policy.source_file)
    return feature_summary
