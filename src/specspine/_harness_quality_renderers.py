from __future__ import annotations

import json

from .harness_models import HarnessQualityReport

__all__ = [
    "render_harness_quality_json",
    "render_harness_quality_text",
]


def render_harness_quality_json(report: HarnessQualityReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_harness_quality_text(report: HarnessQualityReport) -> str:
    lines = [
        f"Harness quality: {report.feature_id}",
        f"Coverage: {report.harness_coverage_pct}%",
        f"Sensors: {report.sensor_count}",
        "",
        "Dimensions:",
    ]
    for dimension in report.governed_dimensions:
        score = report.dimension_scores.get(dimension, 0.0)
        lines.append(f"  - {dimension}: {score}%")

    lines.extend(["", "Safety notes:"])
    lines.append("  - This harness quality report is advisory local evidence.")
    lines.append("  - SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.")

    return "\n".join(lines) + "\n"
