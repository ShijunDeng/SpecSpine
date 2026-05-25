from __future__ import annotations

from typing import Any

from ._matrix_helpers import _checklist_summary

__all__ = [
    "_evidence",
    "_summary",
]


def _evidence(trace: Any, tests: Any, ready: Any) -> dict[str, Any]:
    return {
        "blocking_checks": [check.as_dict() for check in ready.blocking_checks],
        "gaps": [dict(gap) for gap in trace.gaps],
        "has_native_files": tests.has_native_files,
        "missing_files": list(tests.missing_files),
        "quality_checks": [check.as_dict() for check in trace.quality_checks],
        "ready_summary": dict(ready.summary),
        "sources": dict(trace.sources),
        "task_summary": _checklist_summary(trace.tasks),
        "test_coverage_summary": dict(tests.summary["test_coverage"]),
        "test_plan": [item.as_dict() for item in trace.test_plan],
    }


def _summary(matrix: tuple[dict[str, Any], ...], evidence: dict[str, Any]) -> dict[str, Any]:
    verified = sum(1 for row in matrix if row["verification_status"] == "verified")
    total = len(matrix)
    coverage_complete = sum(1 for row in matrix if row["coverage_complete"])
    return {
        "acceptance_criteria": total,
        "blocking_checks": len(evidence["blocking_checks"]),
        "coverage_complete": coverage_complete,
        "coverage_incomplete": total - coverage_complete,
        "gaps": len(evidence["gaps"]),
        "unverified": total - verified,
        "verified": verified,
    }
