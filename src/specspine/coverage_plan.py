from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .coverage_debt import build_coverage_debt_report
from .coverage_utils import (
    _coverage_detail_command,
    _coverage_plan_commands,
    _feature_tests_command,
    _source_files,
)
from .features import (
    FEATURE_FILE_PATHS,
    build_feature_tests_report,
    build_feature_trace_report,
    list_feature_bundles,
    read_feature_metadata,
    validate_feature_slug,
)

__all__ = [
    "_build_feature_coverage_plan_item",
    "_candidate_test_files",
    "_coverage_plan_safety_notes",
    "_missing_feature_plan_report",
    "_risk_note",
    "_suggested_quality_links",
    "build_coverage_plan_report",
    "render_coverage_plan_json",
    "render_coverage_plan_text",
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


def _coverage_plan_safety_notes() -> list[str]:
    return [
        "Coverage plan is read-only and advisory.",
        "Coverage gaps are signals for reviewer follow-up, not proof of test quality.",
        "The command does not write quality files or run tests.",
        "The command does not invoke subprocesses, network services, upstream tools, GitHub APIs, or token providers.",
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
