from __future__ import annotations

from typing import Any

from .status_readiness_helpers import (
    _readiness_next_actions,
    _readiness_detail_command,
)

from ._readiness_record_context import ReadinessRecordContext

__all__ = [
    "build_readiness_record_from_context",
]


def build_readiness_record_from_context(
    ctx: ReadinessRecordContext,
) -> dict[str, Any]:
    blocking_checks = [check.as_dict() for check in ctx.report.blocking_checks]
    gaps = [dict(gap) for gap in ctx.report.gaps]
    record: dict[str, Any] = {
        "feature_id": ctx.report.feature_id,
        "status": ctx.report.status,
        "ready": ctx.report.ready,
        "coverage_required": ctx.coverage_required,
        "policy_coverage_required": ctx.policy_coverage_required,
        "blocking_checks": len(blocking_checks),
        "blocking_check_ids": [check["id"] for check in blocking_checks],
        "gaps": len(gaps),
        "gap_ids": sorted({str(gap["id"]) for gap in gaps}),
        "missing_files": list(ctx.report.missing_files),
        "next_actions": _readiness_next_actions(
            ctx.slug,
            {
                "ready": ctx.report.ready,
                "missing_files": list(ctx.report.missing_files),
                "gaps": gaps,
                "blocking_checks": blocking_checks,
            },
        ),
        "recommended_commands": [
            _readiness_detail_command(
                ctx.slug,
                require_coverage=ctx.require_coverage,
                use_policy=ctx.use_policy,
            )
        ],
    }
    if ctx.use_policy and ctx.policy is not None:
        record["policy_applied"] = True
        record["policy_source"] = str(ctx.policy.source_file)
    return record
