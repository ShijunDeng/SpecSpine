from __future__ import annotations

from typing import Any

from ._model import ReadinessRecordContext
from ._metadata import (
    extract_slug,
    extract_status,
    fetch_feature_metadata,
)
from ._coverage import resolve_coverage_required
from ..features import (
    InvalidFeatureSlug,
    build_feature_ready_report,
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
    slug = extract_slug(feature)
    status = extract_status(feature)

    metadata = fetch_feature_metadata(resolved_root, slug)
    if metadata is None:
        return None

    coverage_required, policy_coverage_required = resolve_coverage_required(
        require_coverage=require_coverage,
        use_policy=use_policy,
        policy=policy,
        feature_id=slug,
        metadata=metadata,
        status=status,
    )

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
