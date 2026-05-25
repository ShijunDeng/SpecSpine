from __future__ import annotations

from .feature_bundle import (
    FeatureHandoffReport,
    _empty_trace_summary,
)
from .feature_handoff_actions import _handoff_next_actions
from .feature_handoff_commands import _recommended_handoff_commands
from ._handoff_build_fetch import HandoffBuildContext

__all__ = [
    "assemble_handoff_report",
]


def assemble_handoff_report(ctx: HandoffBuildContext) -> FeatureHandoffReport:
    next_actions = _handoff_next_actions(
        slug=ctx.slug,
        has_native_files=ctx.has_native_files,
        missing_files=ctx.trace_report.missing_files,
        gaps=ctx.trace_report.gaps,
        tasks=ctx.trace_report.tasks,
        blocking_checks=ctx.ready_report.blocking_checks,
        ready=ctx.ready_report.ready,
    )

    return FeatureHandoffReport(
        feature_id=ctx.slug,
        status=ctx.trace_report.status,
        ready=ctx.ready_report.ready,
        sources=ctx.trace_report.sources,
        missing_files=ctx.trace_report.missing_files,
        gaps=ctx.trace_report.gaps,
        blocking_checks=ctx.ready_report.blocking_checks,
        acceptance_criteria=ctx.trace_report.acceptance_criteria,
        tasks=ctx.trace_report.tasks,
        quality_checks=ctx.trace_report.quality_checks,
        test_plan=ctx.trace_report.test_plan,
        release_readiness=ctx.release_readiness,
        trace_summary=ctx.trace_report.summary if ctx.has_native_files else _empty_trace_summary(),
        ready_summary=ctx.ready_report.summary,
        task_summary=ctx.task_summary,
        recommended_commands=_recommended_handoff_commands(ctx.slug),
        next_actions=next_actions,
        has_native_files=ctx.has_native_files,
        metadata=ctx.metadata,
    )
