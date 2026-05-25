from __future__ import annotations

from pathlib import Path

from ..features import (
    read_feature_metadata,
    build_feature_ready_report,
    build_feature_tests_report,
    build_feature_trace_report,
)
from ._records_coverage import _coverage_state
from .retrospective_commands import _recommended_feature_commands

__all__ = [
    "_feature_record",
]


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
