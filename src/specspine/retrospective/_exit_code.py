from __future__ import annotations

__all__ = [
    "retrospective_report_exit_code",
]


def retrospective_report_exit_code(report: dict[str, object]) -> int:
    summary = report.get("summary", {})
    if isinstance(summary, dict) and summary.get("missing_feature"):
        return 1
    return 0
