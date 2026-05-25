from __future__ import annotations

from typing import Any

from ..policy import WorkspacePolicy
from ..features import read_feature_metadata

__all__ = [
    "_evaluate_policy_coverage",
]


def _evaluate_policy_coverage(
    resolved_root,
    slug: str,
    status: str,
    policy: WorkspacePolicy | None,
) -> bool:
    if policy is None:
        return False
    metadata = read_feature_metadata(resolved_root, slug)
    return policy.require_coverage.requires_coverage(
        feature_id=slug,
        metadata=metadata,
        status=status,
    )
