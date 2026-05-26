from __future__ import annotations

from typing import Any

from .policy import WorkspacePolicy
from ._readiness_record_orchestrator_errors import _is_error_record
from ._phase_metadata_reader import _resolve_phase_metadata
from ._phase_coverage_decision import _compute_coverage_requirement

__all__ = [
    "_resolve_phase_metadata_and_coverage",
]


def _resolve_phase_metadata_and_coverage(
    feature: dict[str, object],
    resolved_root,
    *,
    require_coverage: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
) -> dict[str, Any] | None:
    slug = str(feature["slug"])
    status = str(feature.get("status") or "unknown")

    metadata_or_error = _resolve_phase_metadata(
        feature,
        resolved_root,
        require_coverage=require_coverage,
        use_policy=use_policy,
        policy=policy,
    )
    if _is_error_record(metadata_or_error):
        return metadata_or_error
    metadata = metadata_or_error

    coverage_required, policy_coverage_required = _compute_coverage_requirement(
        feature, metadata, status, require_coverage, policy,
    )

    return {
        "slug": slug,
        "status": status,
        "metadata": metadata,
        "coverage_required": coverage_required,
        "policy_coverage_required": policy_coverage_required,
    }
