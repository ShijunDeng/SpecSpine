from __future__ import annotations

import json

from .feature_bundle import FeatureReadyReport

__all__ = [
    "render_feature_ready_json",
    "render_feature_ready_text",
]


def render_feature_ready_json(report: FeatureReadyReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_ready_text(report: FeatureReadyReport) -> str:
    summary = report.summary
    lines = [
        f"Feature readiness: {report.feature_id}",
        f"Status: {report.status}",
        f"Ready: {'yes' if report.ready else 'no'}",
        (
            "Summary: "
            f"pass={summary['pass']} "
            f"fail={summary['fail']} "
            f"total={summary['total']}"
        ),
        "Blocking checks:",
    ]
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    return "\n".join(lines) + "\n"
