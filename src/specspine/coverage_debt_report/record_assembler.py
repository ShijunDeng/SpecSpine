from __future__ import annotations

from pathlib import Path
from typing import Any

from ..policy import WorkspacePolicy
from ..features import (
    InvalidFeatureSlug,
    FeatureBundleNotFoundError,
)
from ._policy_evaluator import _evaluate_policy_coverage
from ._record_builder import _build_single_feature_record

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
        policy_coverage_required = _evaluate_policy_coverage(
            resolved_root, slug, status, policy
        )
        coverage_required = True if not use_policy else policy_coverage_required
        try:
            records.append(
                _build_single_feature_record(
                    resolved_root,
                    feature,
                    coverage_required=coverage_required,
                    policy_coverage_required=policy_coverage_required,
                    use_policy=use_policy,
                    policy=policy,
                )
            )
        except (InvalidFeatureSlug, FeatureBundleNotFoundError) as error:
            from ..coverage_debt_records import _invalid_coverage_debt_record
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
