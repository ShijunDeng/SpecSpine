from __future__ import annotations

from typing import Any

from .features import (
    InvalidFeatureSlug,
    build_feature_ready_report,
    read_feature_metadata,
)
from .policy import WorkspacePolicy
from .status_readiness_helpers import (
    _readiness_next_actions,
    _readiness_detail_command,
    _invalid_readiness_record,
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

    blocking_checks = [check.as_dict() for check in report.blocking_checks]
    gaps = [dict(gap) for gap in report.gaps]
    record: dict[str, Any] = {
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
    return record
