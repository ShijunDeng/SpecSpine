from __future__ import annotations

from typing import Any

__all__ = [
    "_build_archive_summary",
]


def _build_archive_summary(report: Any) -> dict[str, object]:
    return {
        "blocking_checks": {
            "total": len(report.ready_report.blocking_checks),
        },
        "gaps": {
            "total": len(report.trace_report.gaps),
        },
        "missing_files": {
            "total": len(report.missing_files),
        },
        "ready": dict(report.ready_report.summary),
        "source_files": {
            "total": len(report.source_files),
        },
        "tasks": dict(report.tasks_report.summary),
        "test_coverage": dict(report.tests_report.summary["test_coverage"]),
        "test_plan": dict(report.tests_report.summary["test_plan"]),
        "trace": dict(report.trace_report.summary),
    }
