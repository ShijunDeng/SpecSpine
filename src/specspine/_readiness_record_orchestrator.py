from __future__ import annotations

from typing import Any

from .features import (
    InvalidFeatureSlug,
    build_feature_ready_report,
    read_feature_metadata,
)
from .policy import WorkspacePolicy
from .status_readiness_helpers import _invalid_readiness_record

from ._readiness_record_builder import build_readiness_record_from_context
from ._readiness_record_context import (
    ReadinessRecordContext,
    build_readiness_context,
)

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
    slug = str(feature["slug"])
    status = str(feature.get("status") or "unknown")
    policy_coverage_required = False
    try:
        metadata = read_feature_metadata(resolved_root, slug)
    except InvalidFeatureSlug as error:
        return _invalid_readiness_record(
            feature,
            reason=str(error),
            require_coverage=require_coverage,
            use_policy=use_policy,
            policy=policy,
        )

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
    except InvalidFeatureSlug as error:
        return _invalid_readiness_record(
            feature,
            reason=str(error),
            require_coverage=coverage_required,
            use_policy=use_policy,
            policy_coverage_required=policy_coverage_required,
            policy=policy,
        )

    ctx = ReadinessRecordContext(
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
    return build_readiness_record_from_context(ctx)
