from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .coverage_utils import (
    _coverage_detail_command,
    _feature_tests_command,
    _source_files,
)
from .features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_trace_report,
    feature_bundle_paths,
    list_feature_bundles,
    parse_test_coverage,
    read_feature_metadata,
)
from .policy import WorkspacePolicy, load_workspace_policy

__all__ = [
    "_build_feature_coverage_debt_record",
    "_invalid_coverage_debt_record",
    "build_coverage_debt_report",
    "render_coverage_debt_json",
    "render_coverage_debt_text",
]


def _invalid_coverage_debt_record(
    feature: dict[str, object],
    *,
    coverage_required: bool,
    policy_coverage_required: bool,
    use_policy: bool,
    policy: WorkspacePolicy | None,
    reason: str,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    missing_files = [str(path) for path in feature.get("missing_files", [])]
    record: dict[str, Any] = {
        "acceptance_criteria_total": 0,
        "coverage_required": coverage_required,
        "covered_acceptance_criteria": 0,
        "feature_id": slug,
        "missing_acceptance_criteria": 0,
        "missing_acceptance_criterion_ids": [],
        "missing_files": missing_files,
        "missing_target_link_ids": [],
        "open_coverage_link_ids": [],
        "policy_coverage_required": policy_coverage_required,
        "recommended_commands": [],
        "source_files": _source_files(feature),
        "status": "invalid",
        "unknown_acceptance_criterion_link_ids": [],
    }
    if coverage_required:
        record["recommended_commands"] = [_coverage_detail_command(slug, use_policy=use_policy)]
    if reason:
        record["error"] = reason
    if use_policy and policy is not None:
        record["policy_applied"] = True
        record["policy_source"] = str(policy.source_file)
    return record


def _build_feature_coverage_debt_record(
    root: Path,
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


def build_coverage_debt_report(
    root: Path,
    *,
    use_policy: bool = False,
) -> dict[str, Any]:
    resolved_root = root.expanduser().resolve()
    features = list_feature_bundles(resolved_root)
    policy = load_workspace_policy(resolved_root) if use_policy else None
    records: list[dict[str, Any]] = []

    for feature in features:
        slug = str(feature["slug"])
        status = str(feature.get("status") or "unknown")
        policy_coverage_required = False
        try:
            if policy is not None:
                metadata = read_feature_metadata(resolved_root, slug)
                policy_coverage_required = policy.require_coverage.requires_coverage(
                    feature_id=slug,
                    metadata=metadata,
                    status=status,
                )
            coverage_required = True if not use_policy else policy_coverage_required
            records.append(
                _build_feature_coverage_debt_record(
                    resolved_root,
                    feature,
                    coverage_required=coverage_required,
                    policy_coverage_required=policy_coverage_required,
                    use_policy=use_policy,
                    policy=policy,
                )
            )
        except InvalidFeatureSlug as error:
            records.append(
                _invalid_coverage_debt_record(
                    feature,
                    coverage_required=not use_policy,
                    policy_coverage_required=False,
                    use_policy=use_policy,
                    policy=policy,
                    reason=str(error),
                )
            )
        except FeatureBundleNotFoundError as error:
            records.append(
                _invalid_coverage_debt_record(
                    feature,
                    coverage_required=not use_policy,
                    policy_coverage_required=False,
                    use_policy=use_policy,
                    policy=policy,
                    reason=str(error),
                )
            )

    required_records = [record for record in records if bool(record["coverage_required"])]
    debt_records = [
        record
        for record in required_records
        if int(record["missing_acceptance_criteria"]) > 0
    ]
    recommended_commands = [
        _coverage_detail_command(str(record["feature_id"]), use_policy=use_policy)
        for record in debt_records
    ]
    if not recommended_commands:
        recommended_commands.append("specspine coverage debt . --json")

    summary: dict[str, Any] = {
        "features_skipped": len(records) - len(required_records),
        "missing_target_links": sum(
            len(record["missing_target_link_ids"]) for record in records
        ),
        "open_coverage_links": sum(
            len(record["open_coverage_link_ids"]) for record in records
        ),
        "unknown_acceptance_criterion_links": sum(
            len(record["unknown_acceptance_criterion_link_ids"]) for record in records
        ),
    }
    if use_policy and policy is not None:
        summary["policy_warnings"] = len(policy.require_coverage.warnings)

    report: dict[str, Any] = {
        "acceptance_criteria_total": sum(
            int(record["acceptance_criteria_total"]) for record in required_records
        ),
        "coverage_required_total": len(required_records),
        "covered_acceptance_criteria": sum(
            int(record["covered_acceptance_criteria"]) for record in required_records
        ),
        "features": records,
        "features_total": len(records),
        "features_with_debt": len(debt_records),
        "missing_acceptance_criteria": sum(
            int(record["missing_acceptance_criteria"]) for record in required_records
        ),
        "mode": "policy" if use_policy else "universal",
        "recommended_commands": recommended_commands,
        "root": str(resolved_root),
        "summary": summary,
    }
    if use_policy and policy is not None:
        report["policy_applied"] = True
        report["policy_source"] = str(policy.source_file)
        report["policy_source_missing"] = policy.source_missing
        report["policy_coverage_required_total"] = sum(
            1 for record in records if bool(record["policy_coverage_required"])
        )
    return report


def render_coverage_debt_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_coverage_debt_text(report: dict[str, Any]) -> str:
    lines = [
        f"Coverage debt: {report['root']}",
        f"Mode: {report['mode']}",
        (
            "Features: "
            f"total={report['features_total']} "
            f"coverage_required={report['coverage_required_total']} "
            f"with_debt={report['features_with_debt']}"
        ),
        (
            "Acceptance criteria: "
            f"total={report['acceptance_criteria_total']} "
            f"covered={report['covered_acceptance_criteria']} "
            f"missing={report['missing_acceptance_criteria']}"
        ),
    ]
    summary = report["summary"]
    lines.append(
        "Links: "
        f"open={summary['open_coverage_links']} "
        f"missing_target={summary['missing_target_links']} "
        f"unknown_ac={summary['unknown_acceptance_criterion_links']}"
    )
    if report.get("policy_applied"):
        lines.append(
            "Policy: "
            f"source={report['policy_source']} "
            f"source_missing={'yes' if report['policy_source_missing'] else 'no'}"
        )

    debt_features = [
        feature
        for feature in report["features"]
        if feature["coverage_required"] and feature["missing_acceptance_criteria"]
    ]
    lines.extend(["", "Features with coverage debt:"])
    if not debt_features:
        lines.append("- None.")
    else:
        for feature in debt_features:
            missing_ids = ", ".join(feature["missing_acceptance_criterion_ids"]) or "none"
            lines.append(
                f"- {feature['feature_id']} "
                f"({feature['status']}): "
                f"missing={feature['missing_acceptance_criteria']} "
                f"[{missing_ids}]"
            )
            for command in feature["recommended_commands"]:
                lines.append(f"  command: {command}")

    lines.extend(["", "Recommended commands:"])
    for command in report["recommended_commands"]:
        lines.append(f"- {command}")
    return "\n".join(lines) + "\n"
