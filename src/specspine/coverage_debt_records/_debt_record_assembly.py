from __future__ import annotations

from typing import Any

from ._debt_record_paths import _resolve_feature_paths
from ._debt_record_commands import _build_recommended_commands
from ._debt_coverage_analysis import _analyze_feature_coverage_gaps
from ..coverage_utils import _source_files
from ..policy import WorkspacePolicy

__all__ = [
    "_build_feature_coverage_debt_record",
]


def _build_feature_coverage_debt_record(
    root,
    feature: dict[str, object],
    *,
    coverage_required: bool,
    policy_coverage_required: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    paths, relative_paths = _resolve_feature_paths(slug, root)

    analysis = _analyze_feature_coverage_gaps(
        root,
        slug,
        paths["quality"],
        source_file=relative_paths["quality"],
    )

    trace_report = analysis["trace_report"]
    covered_ids = analysis["covered_ids"]
    missing_ids = analysis["missing_ids"]
    open_link_ids = analysis["open_link_ids"]
    missing_target_link_ids = analysis["missing_target_link_ids"]
    unknown_link_ids = analysis["unknown_link_ids"]

    recommended_commands = _build_recommended_commands(
        slug,
        coverage_required=coverage_required,
        missing_ids=missing_ids,
        use_policy=use_policy,
    )

    record: dict[str, Any] = {
        "acceptance_criteria_total": len(trace_report.acceptance_criteria),
        "coverage_required": coverage_required,
        "covered_acceptance_criteria": len(covered_ids),
        "feature_id": slug,
        "missing_acceptance_criteria": len(missing_ids),
        "missing_acceptance_criterion_ids": missing_ids,
        "missing_files": list(trace_report.missing_files),
        "missing_target_link_ids": missing_target_link_ids,
        "open_coverage_link_ids": open_link_ids,
        "policy_coverage_required": policy_coverage_required,
        "recommended_commands": recommended_commands,
        "source_files": _source_files(feature),
        "status": trace_report.status,
        "unknown_acceptance_criterion_link_ids": unknown_link_ids,
    }
    if use_policy and policy is not None:
        record["policy_applied"] = True
        record["policy_source"] = str(policy.source_file)
    return record
