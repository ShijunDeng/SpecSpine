from __future__ import annotations

from typing import Any

from ..coverage_utils import _coverage_detail_command

__all__ = [
    "_build_summary",
    "_build_recommended_commands",
]


def _build_recommended_commands(
    debt_records: list[dict[str, Any]],
    use_policy: bool,
) -> list[str]:
    recommended_commands = [
        _coverage_detail_command(str(record["feature_id"]), use_policy=use_policy)
        for record in debt_records
    ]
    if not recommended_commands:
        recommended_commands.append("specspine coverage debt . --json")
    return recommended_commands


def _build_summary(
    records: list[dict[str, Any]],
    required_records: list[dict[str, Any]],
    use_policy: bool,
    policy,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "features_skipped": len(records) - len(required_records),
        "missing_target_links": sum(
            len(record["missing_target_link_ids"]) for record in records
        ),
        "open_coverage_links": sum(
            len(record["open_coverage_link_ids"]) for record in records
        ),
        "unknown_acceptance_criterion_links": sum(
            len(record["unknown_acceptance_criterion_link_ids"]) for record in records
        ),
    }
    if use_policy and policy is not None:
        summary["policy_warnings"] = len(policy.require_coverage.warnings)
    return summary
