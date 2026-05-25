from __future__ import annotations

from dataclasses import dataclass

from ._trace_report_serialization import serialize_trace_report
from ._trace_report_summary import compute_trace_summary
from .trace_items import (
    FeatureTask,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
)

__all__ = [
    "FeatureTraceReport",
]


@dataclass(frozen=True)
class FeatureTraceReport:
    feature_id: str
    status: str
    sources: dict[str, dict[str, object]]
    missing_files: tuple[str, ...]
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...]
    tasks: tuple[FeatureTask, ...]
    quality_checks: tuple[FeatureTraceChecklistItem, ...]
    test_plan: tuple[FeatureTraceTestPlanItem, ...]
    gaps: tuple[dict[str, str], ...]

    @property
    def summary(self) -> dict[str, object]:
        return compute_trace_summary(self)

    def as_dict(self) -> dict[str, object]:
        return serialize_trace_report(self)
