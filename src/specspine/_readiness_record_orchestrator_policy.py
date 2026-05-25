from __future__ import annotations

from typing import Any

from .policy import WorkspacePolicy

__all__ = [
    "_resolve_policy_coverage",
]


def _resolve_policy_coverage(
    feature: dict[str, object],
    metadata: dict[str, Any],
    status: str,
    policy: WorkspacePolicy | None,
) -> bool:
    if policy is not None:
        return policy.require_coverage.requires_coverage(
            feature_id=str(feature["slug"]),
            metadata=metadata,
            status=status,
        )
    return False
