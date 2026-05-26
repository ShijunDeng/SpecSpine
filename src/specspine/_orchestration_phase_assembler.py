from __future__ import annotations

from typing import Any

from .policy import WorkspacePolicy
from ._readiness_record_orchestrator_errors import _is_error_record
from ._phase_report_builder import _resolve_phase_report
from ._orchestration_phase_resolver import _resolve_phase_metadata_and_coverage

__all__ = [
    "_resolve_orchestration_phases",
]


def _resolve_orchestration_phases(
    feature: dict[str, object],
    resolved_root,
    *,
    require_coverage: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
) -> dict[str, Any] | None:
    resolved_or_error = _resolve_phase_metadata_and_coverage(
        feature,
        resolved_root,
        require_coverage=require_coverage,
        use_policy=use_policy,
        policy=policy,
    )
    if _is_error_record(resolved_or_error):
        return resolved_or_error
    resolved = resolved_or_error

    report_or_error = _resolve_phase_report(
        feature,
        resolved_root,
        resolved["slug"],
        resolved["status"],
        coverage_required=resolved["coverage_required"],
        use_policy=use_policy,
        policy_coverage_required=resolved["policy_coverage_required"],
        policy=policy,
    )
    if _is_error_record(report_or_error):
        return report_or_error
    report = report_or_error

    return {
        "slug": resolved["slug"],
        "status": resolved["status"],
        "metadata": resolved["metadata"],
        "coverage_required": resolved["coverage_required"],
        "policy_coverage_required": resolved["policy_coverage_required"],
        "report": report,
        "require_coverage": require_coverage,
        "use_policy": use_policy,
        "policy": policy,
    }
