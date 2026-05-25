from __future__ import annotations

from pathlib import Path

from ..features import (
    read_feature_metadata,
    build_feature_ready_report,
    build_feature_tests_report,
    build_feature_trace_report,
)
from .retrospective_commands import _recommended_feature_commands

__all__ = [
    "_coverage_state",
    "_count_by",
    "_feature_record",
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


def _count_by(features: list[dict[str, object]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for feature in features:
        value = str(feature[key])
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _feature_record(root: Path, slug: str) -> dict[str, object]:
    metadata = read_feature_metadata(root, slug)
    trace_report = build_feature_trace_report(root, slug)
    ready_report = build_feature_ready_report(root, slug, require_coverage=True)
    tests_report = build_feature_tests_report(root, slug)
    coverage = _coverage_state(tests_report)
    trace_summary = trace_report.summary
    task_counts = dict(trace_summary["tasks"])  # type: ignore[index]
    readiness_counts = dict(ready_report.summary)
    blocking_checks = [check.as_dict() for check in ready_report.blocking_checks]
    source_files = [
        str(source["path"])
        for source in trace_report.sources.values()
        if bool(source["exists"])
    ]

    return {
        "blocking_checks": blocking_checks,
        "coverage_state": coverage,
        "feature_id": slug,
        "gap_count": len(trace_report.gaps),
        "gaps": [dict(gap) for gap in trace_report.gaps],
        "owner": metadata.owner,
        "priority": metadata.priority,
        "readiness_counts": readiness_counts,
        "ready": ready_report.ready,
        "recommended_commands": _recommended_feature_commands(slug),
        "source_files": source_files,
        "status": ready_report.status,
        "task_counts": task_counts,
    }
