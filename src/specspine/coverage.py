from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_tests_report,
    build_feature_trace_report,
    feature_bundle_paths,
    list_feature_bundles,
    parse_test_coverage,
    read_feature_metadata,
    validate_feature_slug,
)
from .policy import WorkspacePolicy, load_workspace_policy


def _coverage_detail_command(slug: str, *, use_policy: bool) -> str:
    command = f"specspine feature ready {slug} . --json"
    if use_policy:
        return command + " --policy"
    return command + " --require-coverage"


def _feature_tests_command(slug: str) -> str:
    return f"specspine feature tests {slug} . --json"


def _source_files(feature: dict[str, object]) -> list[str]:
    files = feature.get("files", {})
    if not isinstance(files, dict):
        return []
    return sorted(str(path) for path in files.values())


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


def _coverage_plan_safety_notes() -> list[str]:
    return [
        "Coverage plan is read-only and advisory.",
        "Coverage gaps are signals for reviewer follow-up, not proof of test quality.",
        "The command does not write quality files or run tests.",
        "The command does not invoke subprocesses, network services, upstream tools, GitHub APIs, or token providers.",
    ]


def _coverage_plan_commands(slug: str, *, use_policy: bool) -> list[str]:
    ready_command = _coverage_detail_command(slug, use_policy=use_policy)
    return [
        f"specspine feature trace {slug} . --json",
        _feature_tests_command(slug),
        ready_command,
        "specspine validate . --fusion --features",
    ]


def _candidate_test_files(slug: str, record: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    for link in record.get("test_coverage_links", []):
        if not isinstance(link, dict):
            continue
        target_path = str(link.get("target_path") or "")
        if target_path and target_path not in candidates:
            candidates.append(target_path)
    suggested = f"tests/test_{slug.replace('-', '_')}.py"
    if suggested not in candidates:
        candidates.append(suggested)
    return candidates


def _suggested_quality_links(missing_criteria: list[dict[str, Any]]) -> list[str]:
    links: list[str] = []
    for criterion in missing_criteria:
        links.append(f"- [ ] {criterion['id']} -> tests/...")
    return links


def _risk_note(record: dict[str, Any]) -> str:
    notes: list[str] = []
    if record.get("missing_target_link_ids"):
        notes.append("checked coverage links point at missing local targets")
    if record.get("open_coverage_link_ids"):
        notes.append("open coverage links are not counted as coverage")
    if record.get("unknown_acceptance_criterion_link_ids"):
        notes.append("some coverage links reference unknown acceptance criteria")
    if record.get("missing_files"):
        notes.append("the feature bundle is partial")
    if not notes:
        notes.append("acceptance criteria lack checked local Test Coverage links")
    return "; ".join(notes) + "."


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


def build_coverage_plan_report(
    root: Path,
    *,
    use_policy: bool = False,
    feature_filter: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    resolved_root = root.expanduser().resolve()
    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")

    features = list_feature_bundles(resolved_root)
    if feature_filter is not None:
        features = [
            feature for feature in features if str(feature["slug"]) == feature_filter
        ]
        if not features:
            return _missing_feature_plan_report(
                resolved_root,
                feature_filter=feature_filter,
                use_policy=use_policy,
            )

    debt_report = build_coverage_debt_report(resolved_root, use_policy=use_policy)
    debt_records = {
        str(record["feature_id"]): record for record in debt_report["features"]
    }
    selected_records = [
        debt_records[str(feature["slug"])]
        for feature in features
        if str(feature["slug"]) in debt_records
    ]
    required_records = [
        record for record in selected_records if bool(record["coverage_required"])
    ]
    items: list[dict[str, Any]] = []
    for feature in features:
        slug = str(feature["slug"])
        record = debt_records.get(slug)
        if record is None:
            continue
        item = _build_feature_coverage_plan_item(
            resolved_root,
            feature,
            record=record,
            use_policy=use_policy,
        )
        if item is not None:
            items.append(item)

    returned_items = items[:limit] if limit is not None else items
    recommended_commands = [
        f"specspine coverage plan . --feature {item['feature_id']} --json"
        for item in items
    ]
    if not recommended_commands:
        recommended_commands = ["specspine coverage debt . --json"]

    summary = {
        "acceptance_criteria_total": sum(
            int(record["acceptance_criteria_total"]) for record in required_records
        ),
        "coverage_required_total": len(required_records),
        "feature_missing": False,
        "features_scanned": len(features),
        "features_with_plan_items": len(items),
        "items_returned": len(returned_items),
        "items_total": len(items),
        "missing_acceptance_criteria": sum(
            int(record["missing_acceptance_criteria"]) for record in required_records
        ),
    }
    report: dict[str, Any] = {
        "feature_filter": feature_filter,
        "items": returned_items,
        "mode": debt_report["mode"],
        "recommended_commands": recommended_commands,
        "root": str(resolved_root),
        "safety_notes": _coverage_plan_safety_notes(),
        "summary": summary,
    }
    if limit is not None:
        report["limit"] = limit
    if use_policy:
        report["policy_applied"] = debt_report.get("policy_applied", False)
        report["policy_source"] = debt_report.get("policy_source")
        report["policy_source_missing"] = debt_report.get("policy_source_missing", False)
    return report


def render_coverage_plan_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_coverage_plan_text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"Coverage remediation plan: {report['root']}",
        f"Mode: {report['mode']}",
    ]
    if report.get("feature_filter"):
        lines.append(f"Feature filter: {report['feature_filter']}")
    lines.extend(
        [
            (
                "Features: "
                f"scanned={summary['features_scanned']} "
                f"coverage_required={summary['coverage_required_total']} "
                f"with_plan_items={summary['features_with_plan_items']}"
            ),
            (
                "Acceptance criteria: "
                f"total={summary['acceptance_criteria_total']} "
                f"missing={summary['missing_acceptance_criteria']}"
            ),
        ]
    )
    if summary.get("feature_missing"):
        lines.extend(["", f"Missing feature: {report['feature_filter']}"])
        for missing_file in summary.get("missing_files", []):
            lines.append(f"- {missing_file}")

    lines.extend(["", "Plan items:"])
    if not report["items"]:
        lines.append("- None.")
    else:
        for item in report["items"]:
            missing_ids = ", ".join(
                criterion["id"] for criterion in item["missing_acceptance_criteria"]
            )
            lines.append(
                f"- {item['feature_id']} ({item['status']}): "
                f"priority={item['priority']} owner={item['owner']} "
                f"missing=[{missing_ids}]"
            )
            lines.append(f"  risk: {item['risk_note']}")
            for command in item["recommended_commands"]:
                lines.append(f"  command: {command}")

    lines.extend(["", "Safety notes:"])
    for note in report["safety_notes"]:
        lines.append(f"- {note}")
    lines.extend(["", "Recommended commands:"])
    for command in report["recommended_commands"]:
        lines.append(f"- {command}")
    return "\n".join(lines) + "\n"
