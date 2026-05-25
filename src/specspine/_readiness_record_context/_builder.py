from __future__ import annotations

from typing import Any

from ._model import ReadinessRecordContext
from ..features import (
    InvalidFeatureSlug,
    build_feature_ready_report,
    read_feature_metadata,
)
from ..policy import WorkspacePolicy

__all__ = [
    "build_readiness_context",
]


def build_readiness_context(
    feature: dict[str, object],
    resolved_root,
    *,
    require_coverage: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
) -> ReadinessRecordContext | None:
    slug = str(feature["slug"])
    status = str(feature.get("status") or "unknown")
    policy_coverage_required = False
    try:
        metadata = read_feature_metadata(resolved_root, slug)
    except InvalidFeatureSlug:
        return None

    if policy is not None:
        policy_coverage_required = policy.require_coverage.requires_coverage(
            feature_id=slug,
            metadata=metadata,
            status=status,
        )
    coverage_required = require_coverage or policy_coverage_required

    try:
        report = build_feature_ready_report(
            resolved_root,
            slug,
            require_coverage=coverage_required,
            policy_applied=use_policy,
            coverage_required_by_policy=policy_coverage_required,
            policy_source=str(policy.source_file) if policy is not None else None,
        )
    except InvalidFeatureSlug:
        return None

    return ReadinessRecordContext(
        slug=slug,
        status=status,
        metadata=metadata,
        coverage_required=coverage_required,
        policy_coverage_required=policy_coverage_required,
        report=report,
        require_coverage=require_coverage,
        use_policy=use_policy,
        policy=policy,
    )
