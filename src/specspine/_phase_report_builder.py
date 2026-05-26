from __future__ import annotations

from typing import Any

from ._readiness_record_orchestrator_errors import _is_error_record
from ._readiness_record_orchestrator_policy import _resolve_policy_coverage
from ._readiness_record_orchestrator_report import _build_report_or_invalid


def _resolve_phase_report(
    feature: dict[str, object],
    resolved_root,
    slug: str,
    status: str,
    *,
    coverage_required: bool,
    use_policy: bool,
    policy_coverage_required: bool,
    policy,
) -> dict[str, Any] | None:
    """Build report or return error record after resolving policy coverage."""
    report_or_error = _build_report_or_invalid(
        feature,
        resolved_root,
        slug,
        status,
        coverage_required=coverage_required,
        use_policy=use_policy,
        policy_coverage_required=policy_coverage_required,
        policy=policy,
    )
    if _is_error_record(report_or_error):
        return report_or_error
    return report_or_error


__all__ = [
    "_resolve_phase_report",
    "_resolve_policy_coverage",
]
