from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_coverage_debt_json",
    "render_coverage_debt_text",
]


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
