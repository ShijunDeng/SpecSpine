from __future__ import annotations

from typing import Any

from .policy import WorkspacePolicy

from ._readiness_record_orchestrator_phases import _resolve_orchestration_phases
from ._readiness_record_orchestrator_record import _build_record_from_phases
from ._readiness_record_orchestrator_errors import _is_error_record  # noqa: F401

__all__ = [
    "_build_readiness_record",
]


def _build_readiness_record(
    feature: dict[str, object],
    resolved_root,
    *,
    require_coverage: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
) -> dict[str, Any] | None:
    phases = _resolve_orchestration_phases(
        feature,
        resolved_root,
        require_coverage=require_coverage,
        use_policy=use_policy,
        policy=policy,
    )
    if _is_error_record(phases):
        return phases
    return _build_record_from_phases(phases)
