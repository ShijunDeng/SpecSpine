from __future__ import annotations

from typing import Any

from ..coverage_debt_records import (
    _build_feature_coverage_debt_record,
    _invalid_coverage_debt_record,
)

__all__ = [
    "_build_single_feature_record",
]


def _build_single_feature_record(
    resolved_root,
    feature: dict[str, Any],
    coverage_required: bool,
    policy_coverage_required: bool,
    use_policy: bool,
    policy,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    status = str(feature.get("status") or "unknown")
    try:
        return _build_feature_coverage_debt_record(
            resolved_root,
            feature,
            coverage_required=coverage_required,
            policy_coverage_required=policy_coverage_required,
            use_policy=use_policy,
            policy=policy,
        )
    except Exception as error:
        return _invalid_coverage_debt_record(
            feature,
            coverage_required=not use_policy,
            policy_coverage_required=False,
            use_policy=use_policy,
            policy=policy,
            reason=str(error),
        )
