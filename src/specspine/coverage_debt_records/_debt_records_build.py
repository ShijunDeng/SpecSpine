from __future__ import annotations

from typing import Any

from ..coverage_utils import (
    _coverage_detail_command,
    _feature_tests_command,
    _source_files,
)
from ..features import (
    FEATURE_FILE_PATHS,
    feature_bundle_paths,
    build_feature_trace_report,
    parse_test_coverage,
)
from ..policy import WorkspacePolicy

__all__ = [
    "_build_feature_coverage_debt_record",
]


def _build_feature_coverage_debt_record(
    root,
    feature: dict[str, object],
    *,
    coverage_required: bool,
    policy_coverage_required: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    trace_report = build_feature_trace_report(root, slug)
    paths = feature_bundle_paths(root, slug)
    relative_paths = {
        kind: relative_path.format(slug=slug)
        for kind, relative_path in FEATURE_FILE_PATHS.items()
    }

    test_coverage = ()
    quality_path = paths["quality"]
    if quality_path.exists():
        quality_content = quality_path.read_text(encoding="utf-8")
        test_coverage = parse_test_coverage(
            quality_content,
            source_file=relative_paths["quality"],
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

    recommended_commands: list[str] = []
    if coverage_required and missing_ids:
        recommended_commands = [
            _coverage_detail_command(slug, use_policy=use_policy),
            _feature_tests_command(slug),
        ]

    record: dict[str, Any] = {
        "acceptance_criteria_total": len(trace_report.acceptance_criteria),
        "coverage_required": coverage_required,
        "covered_acceptance_criteria": len(covered_ids),
        "feature_id": slug,
        "missing_acceptance_criteria": len(missing_ids),
        "missing_acceptance_criterion_ids": missing_ids,
        "missing_files": list(trace_report.missing_files),
        "missing_target_link_ids": missing_target_link_ids,
        "open_coverage_link_ids": open_link_ids,
        "policy_coverage_required": policy_coverage_required,
        "recommended_commands": recommended_commands,
        "source_files": _source_files(feature),
        "status": trace_report.status,
        "unknown_acceptance_criterion_link_ids": unknown_link_ids,
    }
    if use_policy and policy is not None:
        record["policy_applied"] = True
        record["policy_source"] = str(policy.source_file)
    return record
