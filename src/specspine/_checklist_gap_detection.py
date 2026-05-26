from __future__ import annotations

from .feature_bundle import (
    FeatureTraceChecklistItem,
    FeatureTask,
    FeatureTraceTestPlanItem,
    _trace_gap,
)

__all__ = ["_detect_checklist_gaps"]


def _detect_checklist_gaps(
    spec_file: str,
    execution_file: str,
    quality_file: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    tasks: tuple[FeatureTask, ...],
    quality_checks: tuple[FeatureTraceChecklistItem, ...],
    test_plan: tuple[FeatureTraceTestPlanItem, ...],
) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    if not acceptance_criteria:
        gaps.append(
            _trace_gap(
                "missing_acceptance_criteria",
                spec_file,
                "No acceptance criteria checklist items found.",
            )
        )
    if not tasks:
        gaps.append(
            _trace_gap(
                "missing_tasks",
                execution_file,
                "No task checklist items found.",
            )
        )
    if not quality_checks:
        gaps.append(
            _trace_gap(
                "missing_required_checks",
                quality_file,
                "No required check checklist items found.",
            )
        )
    if not test_plan:
        gaps.append(
            _trace_gap(
                "missing_test_plan",
                quality_file,
                "No non-empty test plan content found.",
            )
        )
    return gaps
