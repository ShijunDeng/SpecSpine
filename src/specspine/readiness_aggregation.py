from __future__ import annotations

from typing import Any

from .status_readiness_helpers import _readiness_detail_command

__all__ = [
    "_aggregate_readiness_summary",
]


def _aggregate_readiness_summary(
    records: list[dict[str, Any]],
    *,
    require_coverage: bool,
    use_policy: bool,
    policy,
) -> dict[str, Any]:
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
