from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._trace_report_model import FeatureTraceReport
    from .trace_items import FeatureTask, FeatureTraceChecklistItem

__all__ = [
    "compute_trace_summary",
]


def compute_trace_summary(report: "FeatureTraceReport") -> dict[str, object]:
    def checklist_counts(
        items: tuple["FeatureTraceChecklistItem", ...] | tuple["FeatureTask", ...],
    ) -> dict[str, int]:
        done = sum(1 for item in items if item.done)
        total = len(items)
        return {
            "done": done,
            "open": total - done,
            "total": total,
        }

    acceptance_criteria = checklist_counts(report.acceptance_criteria)
    tasks = checklist_counts(report.tasks)
    quality_checks = checklist_counts(report.quality_checks)
    total = (
        acceptance_criteria["total"]
        + tasks["total"]
        + quality_checks["total"]
    )
    done = (
        acceptance_criteria["done"]
        + tasks["done"]
        + quality_checks["done"]
    )

    return {
        "acceptance_criteria": acceptance_criteria,
        "done": done,
        "open": total - done,
        "quality_checks": quality_checks,
        "tasks": tasks,
        "test_plan": {"total": len(report.test_plan)},
        "total": total,
    }
