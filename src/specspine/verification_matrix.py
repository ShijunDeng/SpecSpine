from __future__ import annotations

from pathlib import Path
from typing import Any

from .features import feature_bundle_paths


def _checklist_summary(items: tuple[Any, ...]) -> dict[str, int]:
    done = sum(1 for item in items if bool(item.done))
    total = len(items)
    return {
        "done": done,
        "open": total - done,
        "total": total,
    }


def _empty_evidence(root: Path, slug: str) -> dict[str, Any]:
    missing = [
        str(path.relative_to(root))
        for path in feature_bundle_paths(root, slug).values()
    ]
    return {
        "blocking_checks": [],
        "gaps": [
            {
                "id": "missing_file",
                "message": f"Missing native feature file: {relative_path}",
                "source_file": relative_path,
            }
            for relative_path in missing
        ],
        "has_native_files": False,
        "missing_files": missing,
        "quality_checks": [],
        "ready_summary": {"fail": 0, "pass": 0, "total": 0},
        "sources": {
            kind: {
                "exists": False,
                "path": str(path.relative_to(root)),
            }
            for kind, path in feature_bundle_paths(root, slug).items()
        },
        "task_summary": {"done": 0, "open": 0, "total": 0},
        "test_coverage_summary": {"done": 0, "open": 0, "total": 0},
        "test_plan": [],
    }


def _row_gap_reasons(
    *,
    criterion_done: bool,
    coverage_links: list[dict[str, Any]],
    coverage_complete: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not criterion_done:
        reasons.append("acceptance_criterion_open")
    if not coverage_links:
        reasons.append("missing_test_coverage")
    elif not coverage_complete:
        reasons.append("test_coverage_incomplete")
    return tuple(reasons)


def _matrix_rows(trace: Any, tests: Any) -> tuple[dict[str, Any], ...]:
    test_cases_by_ac: dict[str, list[dict[str, Any]]] = {}
    for test_case in tests.test_cases:
        test_cases_by_ac.setdefault(test_case.acceptance_criterion_id, []).append(
            test_case.as_dict()
        )

    coverage_by_ac: dict[str, list[dict[str, Any]]] = {}
    for link in tests.test_coverage:
        coverage_by_ac.setdefault(link.acceptance_criterion_id, []).append(
            link.as_dict()
        )

    rows: list[dict[str, Any]] = []
    for criterion in trace.acceptance_criteria:
        coverage_links = coverage_by_ac.get(criterion.id, [])
        coverage_complete = any(
            bool(link["done"]) and bool(link["target_exists"])
            for link in coverage_links
        )
        reasons = _row_gap_reasons(
            criterion_done=criterion.done,
            coverage_links=coverage_links,
            coverage_complete=coverage_complete,
        )
        rows.append(
            {
                "acceptance_criterion": criterion.as_dict(),
                "coverage_complete": coverage_complete,
                "gap_reasons": list(reasons),
                "test_cases": test_cases_by_ac.get(criterion.id, []),
                "test_coverage": coverage_links,
                "verification_status": (
                    "verified"
                    if criterion.done and coverage_complete
                    else "unverified"
                ),
            }
        )
    return tuple(rows)


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


__all__ = [
    "_checklist_summary",
    "_empty_evidence",
    "_evidence",
    "_matrix_rows",
    "_row_gap_reasons",
    "_summary",
]
