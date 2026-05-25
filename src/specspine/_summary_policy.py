from __future__ import annotations

from typing import Any

from .policy import WorkspacePolicy

__all__ = [
    "_evaluate_policy_coverage",
]


def _evaluate_policy_coverage(
    policy: WorkspacePolicy | None,
    slug: str,
    metadata: Any,
    status: str,
) -> bool:
    if policy is None:
        return False
    return policy.require_coverage.requires_coverage(
        feature_id=slug,
        metadata=metadata,
        status=status,
    )
