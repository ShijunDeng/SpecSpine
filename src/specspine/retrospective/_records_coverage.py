from __future__ import annotations

__all__ = [
    "_coverage_state",
]


def _coverage_state(tests_report: object) -> dict[str, object]:
    acceptance = getattr(tests_report, "acceptance_criteria")
    coverage = getattr(tests_report, "test_coverage")
    total = len(acceptance)
    completed_links = [
        link for link in coverage if link.done and link.target_exists
    ]
    covered_ids = {
        link.acceptance_criterion_id
        for link in completed_links
    }
    missing_ids = [
        item.id for item in acceptance if item.id not in covered_ids
    ]
    if total == 0:
        state = "not_applicable"
    elif not coverage:
        state = "missing"
    elif missing_ids:
        state = "partial"
    else:
        state = "complete"
    return {
        "completed_links": len(completed_links),
        "missing_acceptance_criteria": missing_ids,
        "state": state,
        "total_acceptance_criteria": total,
        "total_links": len(coverage),
    }
