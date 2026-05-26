from __future__ import annotations

from typing import Any

from ..policy import WorkspacePolicy

__all__ = [
    "resolve_coverage_required",
]


def resolve_coverage_required(
    *,
    require_coverage: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
    feature_id: str,
    metadata: Any,
    status: str,
) -> tuple[bool, bool]:
    policy_coverage_required = False
    if policy is not None:
        policy_coverage_required = policy.require_coverage.requires_coverage(
            feature_id=feature_id,
            metadata=metadata,
            status=status,
        )
    coverage_required = require_coverage or policy_coverage_required
    return coverage_required, policy_coverage_required
