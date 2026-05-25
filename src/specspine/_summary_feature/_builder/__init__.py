from __future__ import annotations

from typing import Any

from ...policy import WorkspacePolicy
from .._context import _resolve_feature_context
from ._report_gathering import _gather_feature_report
from ._summary_assembly import _assemble_feature_summary

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

    result = _gather_feature_report(
        resolved_root,
        context["slug"],
        context["summary_require_coverage"],
        feature,
        require_coverage=context["summary_require_coverage"],
        policy=policy,
        policy_coverage_required=context["policy_coverage_required"],
    )

    if "report" not in result:
        return result

    return _assemble_feature_summary(
        result["report"],
        context["metadata"],
        feature,
        context,
        policy,
    )
