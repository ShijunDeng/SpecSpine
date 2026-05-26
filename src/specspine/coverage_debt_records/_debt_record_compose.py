from __future__ import annotations

from typing import Any

from ._debt_record_commands import _build_recommended_commands
from ..coverage_utils import _source_files
from ..policy import WorkspacePolicy


def _compose_debt_record(
    slug: str,
    trace_report,
    covered_ids: list,
    missing_ids: list,
    open_link_ids: list,
    missing_target_link_ids: list,
    unknown_link_ids: list,
    *,
    coverage_required: bool,
    policy_coverage_required: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
    feature: dict[str, object],
) -> dict[str, Any]:
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


__all__ = [
    "_compose_debt_record",
]
