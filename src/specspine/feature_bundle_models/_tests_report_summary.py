from __future__ import annotations

from .trace import FeatureTraceChecklistItem, FeatureTestCoverageLink

__all__ = [
    "checklist_counts",
    "compute_tests_report_summary",
]


def checklist_counts(
    items: tuple[FeatureTraceChecklistItem, ...],
) -> dict[str, int]:
    done = sum(1 for item in items if item.done)
    total = len(items)
    return {
        "done": done,
        "open": total - done,
        "total": total,
    }


def compute_tests_report_summary(report) -> dict[str, object]:
    return {
        "acceptance_criteria": checklist_counts(report.acceptance_criteria),
        "blocking_checks": {"total": len(report.blocking_checks)},
        "gaps": {"total": len(report.gaps)},
        "missing_files": {"total": len(report.missing_files)},
        "quality_checks": checklist_counts(report.quality_checks),
        "ready": dict(report.ready_summary),
        "source_files": {"total": len(report.source_files)},
        "test_cases": {"total": len(report.test_cases)},
        "test_coverage": checklist_counts(report.test_coverage),
        "test_plan": {"total": len(report.test_plan)},
    }
