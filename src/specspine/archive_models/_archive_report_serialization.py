from __future__ import annotations

from typing import Any

__all__ = [
    "_build_archive_dict",
]


def _build_archive_dict(report: Any) -> dict[str, object]:
    payload: dict[str, object] = {
        "archive_id": report.archive_id,
        "coverage_required": report.coverage_required,
        "feature_id": report.feature_id,
        "metadata": dict(report.metadata),
        "missing_files": list(report.missing_files),
        "ready": report.ready,
        "ready_report": report.ready_report.as_dict(),
        "recommended_commands": list(report.recommended_commands),
        "safety_notes": list(report.safety_notes),
        "source_files": list(report.source_files),
        "status": report.status,
        "summary": report.summary,
        "tasks_report": report.tasks_report.as_dict(),
        "tests_report": report.tests_report.as_dict(),
        "trace_report": report.trace_report.as_dict(),
    }
    if report.package is not None:
        payload["package"] = report.package.as_dict()
    return payload
