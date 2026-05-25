from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_coverage_plan_json",
    "render_coverage_plan_text",
]


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
