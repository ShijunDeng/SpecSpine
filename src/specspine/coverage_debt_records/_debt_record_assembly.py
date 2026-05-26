from __future__ import annotations

from typing import Any

from ._debt_record_gather import _gather_debt_analysis
from ._debt_record_compose import _compose_debt_record
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

    gathered = _gather_debt_analysis(root, slug)

    return _compose_debt_record(
        slug,
        gathered["trace_report"],
        gathered["covered_ids"],
        gathered["missing_ids"],
        gathered["open_link_ids"],
        gathered["missing_target_link_ids"],
        gathered["unknown_link_ids"],
        coverage_required=coverage_required,
        policy_coverage_required=policy_coverage_required,
        use_policy=use_policy,
        policy=policy,
        feature=feature,
    )
