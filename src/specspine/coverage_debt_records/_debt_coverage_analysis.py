from __future__ import annotations

from ..features import build_feature_trace_report, parse_test_coverage

__all__ = [
    "_analyze_feature_coverage_gaps",
]


def _analyze_feature_coverage_gaps(
    root,
    slug: str,
    quality_path,
    *,
    source_file: str,
) -> dict:
    trace_report = build_feature_trace_report(root, slug)

    test_coverage = ()
    if quality_path.exists():
        quality_content = quality_path.read_text(encoding="utf-8")
        test_coverage = parse_test_coverage(
            quality_content,
            source_file=source_file,
            root=root,
        )

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
        "trace_report": trace_report,
        "criterion_ids": criterion_ids,
        "covered_ids": covered_ids,
        "missing_ids": missing_ids,
        "open_link_ids": open_link_ids,
        "missing_target_link_ids": missing_target_link_ids,
        "unknown_link_ids": unknown_link_ids,
        "test_coverage": test_coverage,
    }
