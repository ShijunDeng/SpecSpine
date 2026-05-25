from __future__ import annotations

from typing import Any

from .policy import WorkspacePolicy

from ._readiness_record_orchestrator_errors import _is_error_record
from ._readiness_record_orchestrator_policy import _resolve_policy_coverage
from ._readiness_record_orchestrator_report import (
    _build_report_or_invalid,
    _read_metadata_or_invalid,
)

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
    slug = str(feature["slug"])
    status = str(feature.get("status") or "unknown")

    metadata_or_error = _read_metadata_or_invalid(
        feature,
        resolved_root,
        require_coverage=require_coverage,
        use_policy=use_policy,
        policy=policy,
    )
    if _is_error_record(metadata_or_error):
        return metadata_or_error
    metadata = metadata_or_error

    policy_coverage_required = _resolve_policy_coverage(feature, metadata, status, policy)
    coverage_required = require_coverage or policy_coverage_required

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
    report = report_or_error

    return {
        "slug": slug,
        "status": status,
        "metadata": metadata,
        "coverage_required": coverage_required,
        "policy_coverage_required": policy_coverage_required,
        "report": report,
        "require_coverage": require_coverage,
        "use_policy": use_policy,
        "policy": policy,
    }
