from __future__ import annotations

from ._handoff_report_model import FeatureHandoffReport

__all__ = [
    "get_handoff_summary",
]


def get_handoff_summary(report: FeatureHandoffReport) -> dict[str, object]:
    return {
        "blocking_checks": {"total": len(report.blocking_checks)},
        "gaps": {"total": len(report.gaps)},
        "ready": dict(report.ready_summary),
        "tasks": dict(report.task_summary),
        "trace": dict(report.trace_summary),
    }
