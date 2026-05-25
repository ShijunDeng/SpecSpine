from __future__ import annotations

from typing import TYPE_CHECKING

from ._trace_report_summary import compute_trace_summary

if TYPE_CHECKING:
    from ._trace_report_model import FeatureTraceReport

__all__ = [
    "serialize_trace_report",
]


def serialize_trace_report(report: "FeatureTraceReport") -> dict[str, object]:
    return {
        "acceptance_criteria": [
            item.as_dict() for item in report.acceptance_criteria
        ],
        "feature_id": report.feature_id,
        "gaps": [dict(gap) for gap in report.gaps],
        "missing_files": list(report.missing_files),
        "quality_checks": [item.as_dict() for item in report.quality_checks],
        "sources": report.sources,
        "status": report.status,
        "summary": compute_trace_summary(report),
        "tasks": [task.as_dict() for task in report.tasks],
        "test_plan": [item.as_dict() for item in report.test_plan],
    }
