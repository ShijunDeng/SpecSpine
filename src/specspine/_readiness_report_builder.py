from __future__ import annotations

from typing import Any

from .features import (
    InvalidFeatureSlug,
    build_feature_ready_report,
)
from .policy import WorkspacePolicy
from .status_readiness_helpers import _invalid_readiness_record

__all__ = [
    "_build_report_or_invalid",
]


def _build_report_or_invalid(
    feature: dict[str, object],
    resolved_root,
    slug: str,
    status: str,
    *,
    coverage_required: bool,
    use_policy: bool,
    policy_coverage_required: bool,
    policy: WorkspacePolicy | None,
) -> dict[str, Any] | None:
    try:
        return build_feature_ready_report(
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
