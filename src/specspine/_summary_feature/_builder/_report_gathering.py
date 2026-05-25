from __future__ import annotations

from typing import Any

from ...features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_handoff_report,
)
from ...policy import WorkspacePolicy
from ...status_features_helpers import (
    _invalid_feature_summary,
    _missing_feature_summary,
)

__all__ = [
    "_gather_feature_report",
]


def _gather_feature_report(
    resolved_root: Any,
    slug: str,
    summary_require_coverage: bool,
    feature: dict[str, object],
    *,
    require_coverage: bool,
    policy: WorkspacePolicy | None,
    policy_coverage_required: bool,
) -> dict[str, Any] | None:
    try:
        report = build_feature_handoff_report(
            resolved_root,
            slug,
            require_coverage=summary_require_coverage,
        )
        return {"report": report}
    except InvalidFeatureSlug as error:
        return _invalid_feature_summary(
            feature,
            reason=str(error),
            require_coverage=require_coverage,
            policy=policy,
            policy_coverage_required=policy_coverage_required,
        )
    except FeatureBundleNotFoundError:
        return _missing_feature_summary(
            feature,
            require_coverage=require_coverage,
            policy=policy,
            policy_coverage_required=policy_coverage_required,
        )
