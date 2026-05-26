from __future__ import annotations

from typing import Any

from .features import (
    InvalidFeatureSlug,
    read_feature_metadata,
)
from .policy import WorkspacePolicy
from .status_readiness_helpers import _invalid_readiness_record

__all__ = [
    "_read_metadata_or_invalid",
]


def _read_metadata_or_invalid(
    feature: dict[str, object],
    resolved_root,
    *,
    require_coverage: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
) -> dict[str, Any] | None:
    slug = str(feature["slug"])
    try:
        return read_feature_metadata(resolved_root, slug)
    except InvalidFeatureSlug as error:
        return _invalid_readiness_record(
            feature,
            reason=str(error),
            require_coverage=require_coverage,
            use_policy=use_policy,
            policy=policy,
        )
