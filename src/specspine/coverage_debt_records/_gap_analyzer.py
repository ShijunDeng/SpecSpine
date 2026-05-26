from __future__ import annotations

__all__ = [
    "_compute_coverage_gaps",
]


def _compute_coverage_gaps(
    trace_report,
    test_coverage: tuple,
) -> dict:
    criterion_ids = {criterion.id for criterion in trace_report.acceptance_criteria}
    covered_ids = {
        link.acceptance_criterion_id
        for link in test_coverage
        if link.acceptance_criterion_id in criterion_ids
        and link.done
        and link.target_exists
    }
    missing_ids = [
        criterion.id
        for criterion in trace_report.acceptance_criteria
        if criterion.id not in covered_ids
    ]
    open_link_ids = [
        link.id
        for link in test_coverage
        if link.acceptance_criterion_id in criterion_ids and not link.done
    ]
    missing_target_link_ids = [
        link.id
        for link in test_coverage
        if link.done and not link.target_exists
    ]
    unknown_link_ids = [
        link.id
        for link in test_coverage
        if link.acceptance_criterion_id not in criterion_ids
    ]

    return {
        "criterion_ids": criterion_ids,
        "covered_ids": covered_ids,
        "missing_ids": missing_ids,
        "open_link_ids": open_link_ids,
        "missing_target_link_ids": missing_target_link_ids,
        "unknown_link_ids": unknown_link_ids,
    }
