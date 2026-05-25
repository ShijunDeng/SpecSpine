from __future__ import annotations

from pathlib import Path
from typing import Any

from ..coverage_utils import (
    _coverage_plan_commands,
    _source_files,
)
from ..features import (
    FEATURE_FILE_PATHS,
    build_feature_tests_report,
    build_feature_trace_report,
    read_feature_metadata,
)
from ._plan_items_helpers import (
    _candidate_test_files,
    _coverage_plan_safety_notes,
    _risk_note,
    _suggested_quality_links,
)

__all__ = [
    "_build_feature_coverage_plan_item",
    "_missing_feature_plan_report",
]


def _missing_feature_plan_report(
    root: Path,
    *,
    feature_filter: str,
    use_policy: bool,
) -> dict[str, Any]:
    resolved_root = root.expanduser().resolve()
    missing_files = [
        relative_path.format(slug=feature_filter)
        for relative_path in FEATURE_FILE_PATHS.values()
    ]
    return {
        "error": "feature_not_found",
        "feature_filter": feature_filter,
        "items": [],
        "mode": "policy" if use_policy else "universal",
        "recommended_commands": [
            f"specspine feature new {feature_filter} .",
            "specspine coverage plan . --json",
        ],
        "root": str(resolved_root),
        "safety_notes": _coverage_plan_safety_notes(),
        "summary": {
            "acceptance_criteria_total": 0,
            "coverage_required_total": 0,
            "feature_missing": True,
            "features_scanned": 0,
            "features_with_plan_items": 0,
            "items_returned": 0,
            "items_total": 0,
            "missing_acceptance_criteria": 0,
            "missing_files": missing_files,
        },
    }


def _build_feature_coverage_plan_item(
    root: Path,
    feature: dict[str, object],
    *,
    record: dict[str, Any],
    use_policy: bool,
) -> dict[str, Any] | None:
    slug = str(feature["slug"])
    if not bool(record["coverage_required"]) or int(record["missing_acceptance_criteria"]) <= 0:
        return None

    trace_report = build_feature_trace_report(root, slug)
    metadata = read_feature_metadata(root, slug)
    missing_ids = set(record["missing_acceptance_criterion_ids"])
    missing_criteria = [
        {
            "id": criterion.id,
            "line": criterion.line,
            "source_file": criterion.source_file,
            "text": criterion.text,
        }
        for criterion in trace_report.acceptance_criteria
        if criterion.id in missing_ids
    ]
    tests_report = build_feature_tests_report(root, slug)
    record["test_coverage_links"] = [
        link.as_dict() for link in tests_report.test_coverage
    ]
    commands = _coverage_plan_commands(slug, use_policy=use_policy)
    return {
        "candidate_test_files": _candidate_test_files(slug, record),
        "feature_id": slug,
        "missing_acceptance_criteria": missing_criteria,
        "owner": metadata.owner,
        "priority": metadata.priority,
        "recommended_commands": commands,
        "risk_note": _risk_note(record),
        "status": trace_report.status,
        "suggested_quality_links": _suggested_quality_links(missing_criteria),
    }
