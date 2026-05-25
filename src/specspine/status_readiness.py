from __future__ import annotations

from pathlib import Path
from typing import Any

from .features import (
    InvalidFeatureSlug,
    build_feature_ready_report,
    list_feature_bundles,
    read_feature_metadata,
)
from .policy import WorkspacePolicy, load_workspace_policy
from .status_workspace import _empty_count_summary
from .status_readiness_helpers import (
    _readiness_next_actions,
    _readiness_detail_command,
    _invalid_readiness_record,
)

__all__ = [
    "_readiness_next_actions",
    "_readiness_detail_command",
    "_invalid_readiness_record",
    "build_readiness_summary",
]


def build_readiness_summary(
    root: Path,
    features: list[dict[str, object]] | None = None,
    *,
    require_coverage: bool = False,
    use_policy: bool = False,
) -> dict[str, Any]:
    resolved_root = root.expanduser().resolve()
    feature_bundles = features if features is not None else list_feature_bundles(resolved_root)
    policy = load_workspace_policy(resolved_root) if use_policy else None
    records: list[dict[str, Any]] = []

    for feature in feature_bundles:
        slug = str(feature["slug"])
        status = str(feature.get("status") or "unknown")
        policy_coverage_required = False
        try:
            metadata = read_feature_metadata(resolved_root, slug)
        except InvalidFeatureSlug as error:
            records.append(
                _invalid_readiness_record(
                    feature,
                    reason=str(error),
                    require_coverage=require_coverage,
                    use_policy=use_policy,
                    policy=policy,
                )
            )
            continue

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
            records.append(
                _invalid_readiness_record(
                    feature,
                    reason=str(error),
                    require_coverage=coverage_required,
                    use_policy=use_policy,
                    policy_coverage_required=policy_coverage_required,
                    policy=policy,
                )
            )
            continue

        blocking_checks = [check.as_dict() for check in report.blocking_checks]
        gaps = [dict(gap) for gap in report.gaps]
        record = {
            "feature_id": report.feature_id,
            "status": report.status,
            "ready": report.ready,
            "coverage_required": coverage_required,
            "policy_coverage_required": policy_coverage_required,
            "blocking_checks": len(blocking_checks),
            "blocking_check_ids": [check["id"] for check in blocking_checks],
            "gaps": len(gaps),
            "gap_ids": sorted({str(gap["id"]) for gap in gaps}),
            "missing_files": list(report.missing_files),
            "next_actions": _readiness_next_actions(
                slug,
                {
                    "ready": report.ready,
                    "missing_files": list(report.missing_files),
                    "gaps": gaps,
                    "blocking_checks": blocking_checks,
                },
            ),
            "recommended_commands": [
                _readiness_detail_command(
                    slug,
                    require_coverage=require_coverage,
                    use_policy=use_policy,
                )
            ],
        }
        if use_policy and policy is not None:
            record["policy_applied"] = True
            record["policy_source"] = str(policy.source_file)
        records.append(record)

    ready_count = sum(1 for record in records if record["ready"])
    not_ready_records = [record for record in records if not record["ready"]]
    recommended_commands = [
        _readiness_detail_command(
            str(record["feature_id"]),
            require_coverage=require_coverage,
            use_policy=use_policy,
        )
        for record in not_ready_records
    ]
    if not recommended_commands:
        recommended_commands.append("specspine status . --json --readiness-summary")

    summary: dict[str, Any] = {
        "features_total": len(records),
        "ready": ready_count,
        "not_ready": len(records) - ready_count,
        "blocking_checks_total": sum(int(record["blocking_checks"]) for record in records),
        "gaps_total": sum(int(record["gaps"]) for record in records),
        "coverage_required_total": sum(
            1 for record in records if bool(record["coverage_required"])
        ),
        "features": records,
        "recommended_commands": recommended_commands,
    }
    if use_policy and policy is not None:
        summary["policy_applied"] = True
        summary["policy_source"] = str(policy.source_file)
        summary["policy_source_missing"] = policy.source_missing
        summary["policy_coverage_required_total"] = sum(
            1 for record in records if bool(record["policy_coverage_required"])
        )
    return summary
