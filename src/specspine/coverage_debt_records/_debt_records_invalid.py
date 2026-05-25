from __future__ import annotations

from typing import Any

from ..coverage_utils import (
    _coverage_detail_command,
    _source_files,
)
from ..policy import WorkspacePolicy

__all__ = [
    "_invalid_coverage_debt_record",
]


def _invalid_coverage_debt_record(
    feature: dict[str, object],
    *,
    coverage_required: bool,
    policy_coverage_required: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
    reason: str,
) -> dict[str, Any]:
    from ..features import build_feature_trace_report

    slug = str(feature["slug"])
    missing_files = [str(path) for path in feature.get("missing_files", [])]
    record: dict[str, Any] = {
        "acceptance_criteria_total": 0,
        "coverage_required": coverage_required,
        "covered_acceptance_criteria": 0,
        "feature_id": slug,
        "missing_acceptance_criteria": 0,
        "missing_acceptance_criterion_ids": [],
        "missing_files": missing_files,
        "missing_target_link_ids": [],
        "open_coverage_link_ids": [],
        "policy_coverage_required": policy_coverage_required,
        "recommended_commands": [],
        "source_files": _source_files(feature),
        "status": "invalid",
        "unknown_acceptance_criterion_link_ids": [],
    }
    if coverage_required:
        record["recommended_commands"] = [_coverage_detail_command(slug, use_policy=use_policy)]
    if reason:
        record["error"] = reason
    if use_policy and policy is not None:
        record["policy_applied"] = True
        record["policy_source"] = str(policy.source_file)
    return record
