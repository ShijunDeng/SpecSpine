from __future__ import annotations

from typing import Any

from .policy import WorkspacePolicy
from ._phase_report_builder import _resolve_policy_coverage


def _compute_coverage_requirement(
    feature: dict[str, object],
    metadata: dict[str, Any],
    status: str,
    require_coverage: bool,
    policy: WorkspacePolicy | None,
) -> tuple[bool, bool]:
    policy_coverage_required = _resolve_policy_coverage(feature, metadata, status, policy)
    coverage_required = require_coverage or policy_coverage_required
    return coverage_required, policy_coverage_required


__all__ = [
    "_compute_coverage_requirement",
]
