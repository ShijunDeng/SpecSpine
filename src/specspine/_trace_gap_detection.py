from __future__ import annotations

from .feature_bundle import (
    FeatureTraceChecklistItem,
    FeatureTask,
    FeatureTraceTestPlanItem,
)
from ._file_gap_detection import _detect_file_gaps
from ._checklist_gap_detection import _detect_checklist_gaps

__all__ = [
    "_detect_trace_gaps",
]


def _detect_trace_gaps(
    missing_files: list[str],
    spec_file: str,
    execution_file: str,
    quality_file: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    tasks: tuple[FeatureTask, ...],
    quality_checks: tuple[FeatureTraceChecklistItem, ...],
    test_plan: tuple[FeatureTraceTestPlanItem, ...],
) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    gaps.extend(_detect_file_gaps(missing_files))
    gaps.extend(
        _detect_checklist_gaps(
            spec_file,
            execution_file,
            quality_file,
            acceptance_criteria,
            tasks,
            quality_checks,
            test_plan,
        )
    )
    return gaps
