from __future__ import annotations

from typing import Any

from ..features import InvalidFeatureSlug, read_feature_metadata
from ..policy import WorkspacePolicy
from ..status_workspace import _empty_feature_metadata
from .._summary_policy import _evaluate_policy_coverage

__all__ = [
    "_resolve_feature_context",
]


def _resolve_feature_context(
    resolved_root: Any,
    feature: dict[str, object],
    *,
    require_coverage: bool,
    policy: WorkspacePolicy | None,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    status = str(feature.get("status") or "unknown")
    try:
        metadata = read_feature_metadata(resolved_root, slug)
    except InvalidFeatureSlug:
        metadata = _empty_feature_metadata()

    policy_coverage_required = _evaluate_policy_coverage(
        policy, slug, metadata, status,
    )
    summary_require_coverage = require_coverage or policy_coverage_required

    return {
        "slug": slug,
        "status": status,
        "metadata": metadata,
        "summary_require_coverage": summary_require_coverage,
        "policy_coverage_required": policy_coverage_required,
    }
