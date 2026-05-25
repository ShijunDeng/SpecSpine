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
    list_feature_bundles,
    read_feature_metadata,
)
from ..policy import WorkspacePolicy, load_workspace_policy
from .summary import _build_summary, _build_recommended_commands

__all__ = [
    "build_coverage_debt_report",
]


def build_coverage_debt_report(
    root: Path,
    *,
    use_policy: bool = False,
) -> dict[str, Any]:
    resolved_root = root.expanduser().resolve()
    features = list_feature_bundles(resolved_root)
    policy = load_workspace_policy(resolved_root) if use_policy else None
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

    required_records = [record for record in records if bool(record["coverage_required"])]
    debt_records = [
        record
        for record in required_records
        if int(record["missing_acceptance_criteria"]) > 0
    ]
    recommended_commands = _build_recommended_commands(debt_records, use_policy)

    summary = _build_summary(records, required_records, use_policy, policy)

    report: dict[str, Any] = {
        "acceptance_criteria_total": sum(
            int(record["acceptance_criteria_total"]) for record in required_records
        ),
        "coverage_required_total": len(required_records),
        "covered_acceptance_criteria": sum(
            int(record["covered_acceptance_criteria"]) for record in required_records
        ),
        "features": records,
        "features_total": len(records),
        "features_with_debt": len(debt_records),
        "missing_acceptance_criteria": sum(
            int(record["missing_acceptance_criteria"]) for record in required_records
        ),
        "mode": "policy" if use_policy else "universal",
        "recommended_commands": recommended_commands,
        "root": str(resolved_root),
        "summary": summary,
    }
    if use_policy and policy is not None:
        report["policy_applied"] = True
        report["policy_source"] = str(policy.source_file)
        report["policy_source_missing"] = policy.source_missing
        report["policy_coverage_required_total"] = sum(
            1 for record in records if bool(record["policy_coverage_required"])
        )
    return report
