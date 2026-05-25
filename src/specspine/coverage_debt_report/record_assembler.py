from __future__ import annotations

from pathlib import Path
from typing import Any

from ..coverage_debt_records import (
    _build_feature_coverage_debt_record,
    _invalid_coverage_debt_record,
)
from ..features import (
    InvalidFeatureSlug,
    FeatureBundleNotFoundError,
    read_feature_metadata,
)
from ..policy import WorkspacePolicy

__all__ = [
    "_build_all_feature_records",
]


def _build_all_feature_records(
    resolved_root: Path,
    features: list[dict[str, Any]],
    policy: WorkspacePolicy | None,
    use_policy: bool,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for feature in features:
        slug = str(feature["slug"])
        status = str(feature.get("status") or "unknown")
        policy_coverage_required = False
        try:
            if policy is not None:
                metadata = read_feature_metadata(resolved_root, slug)
                policy_coverage_required = policy.require_coverage.requires_coverage(
                    feature_id=slug,
                    metadata=metadata,
                    status=status,
                )
            coverage_required = True if not use_policy else policy_coverage_required
            records.append(
                _build_feature_coverage_debt_record(
                    resolved_root,
                    feature,
                    coverage_required=coverage_required,
                    policy_coverage_required=policy_coverage_required,
                    use_policy=use_policy,
                    policy=policy,
                )
            )
        except InvalidFeatureSlug as error:
            records.append(
                _invalid_coverage_debt_record(
                    feature,
                    coverage_required=not use_policy,
                    policy_coverage_required=False,
                    use_policy=use_policy,
                    policy=policy,
                    reason=str(error),
                )
            )
        except FeatureBundleNotFoundError as error:
            records.append(
                _invalid_coverage_debt_record(
                    feature,
                    coverage_required=not use_policy,
                    policy_coverage_required=False,
                    use_policy=use_policy,
                    policy=policy,
                    reason=str(error),
                )
            )

    return records
