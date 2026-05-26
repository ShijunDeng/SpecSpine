from __future__ import annotations

from typing import Any

from ._readiness_record_orchestrator_report import _read_metadata_or_invalid
from ._readiness_record_orchestrator_errors import _is_error_record


def _resolve_phase_metadata(
    feature: dict[str, object],
    resolved_root,
    *,
    require_coverage: bool,
    use_policy: bool,
    policy,
) -> dict[str, Any] | None:
    """Read and validate feature metadata, returning error record or metadata."""
    metadata_or_error = _read_metadata_or_invalid(
        feature,
        resolved_root,
        require_coverage=require_coverage,
        use_policy=use_policy,
        policy=policy,
    )
    if _is_error_record(metadata_or_error):
        return metadata_or_error
    return metadata_or_error


__all__ = [
    "_resolve_phase_metadata",
]
