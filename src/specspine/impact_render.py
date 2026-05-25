from __future__ import annotations

import json

from .impact_models import TestImpactReport


def render_test_impact_json(report: TestImpactReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_test_impact_text(report: TestImpactReport) -> str:
    summary = report.summary
    lines = [
        f"Test impact packet: {report.root}",
        (
            "Summary: "
            f"source_modules={summary['source_modules']} "
            f"test_files={summary['test_files']} "
            f"tests_with_source_links={summary['tests_with_source_links']} "
            f"changed_files={summary['changed_files']} "
            f"fallbacks={summary['fallback_recommendations']}"
        ),
        "",
        "Changed files:",
    ]
    if report.changed_files:
        lines.extend(f"- {path}" for path in report.changed_files)
    else:
        lines.append("- None provided.")

    if report.feature is not None:
        feature = report.feature
        lines.extend(
            [
                "",
                "Feature coverage:",
                (
                    f"- {feature['feature_id']} "
                    f"status={feature['status']} "
                    f"ready={'yes' if feature['ready'] else 'no'} "
                    f"coverage_targets={len(feature['coverage_targets'])}"
                ),
            ]
        )
        if feature["missing_files"]:
            lines.extend(f"- missing {path}" for path in feature["missing_files"])

    lines.extend(["", "Recommendations:"])
    for recommendation in report.recommendations:
        marker = "fallback" if recommendation["fallback"] else "direct"
        tests = ", ".join(recommendation["test_files"]) or "none"
        lines.append(f"- [{marker}] {recommendation['command']}")
        lines.append(f"  reason: {recommendation['reason']}")
        lines.append(f"  tests: {tests}")

    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report.safety_notes)
    return "\n".join(lines) + "\n"


__all__ = [
    "render_test_impact_json",
    "render_test_impact_text",
]
