from __future__ import annotations

from typing import Any

__all__ = [
    "_row_gap_reasons",
    "_matrix_rows",
]


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
