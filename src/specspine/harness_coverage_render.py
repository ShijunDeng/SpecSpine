from __future__ import annotations

import json

from .harness_coverage_models import (
    MATURITY_LABELS,
    HarnessCoverageReport,
)

__all__ = [
    "render_harness_coverage_json",
    "render_harness_coverage_text",
]


def render_harness_coverage_json(report: HarnessCoverageReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_harness_coverage_text(report: HarnessCoverageReport) -> str:
    lines = [
        f"Harness coverage: {report.feature_id}",
        f"Maturity: {report.maturity_score} ({MATURITY_LABELS.get(report.maturity_score, 'unknown')})",
        "",
        "Dimensions:",
    ]
    for d in report.dimensions:
        status = "pass" if d.coverage_pct >= 100 else "partial" if d.coverage_pct > 0 else "missing"
        lines.append(
            f"  [{status}] {d.dimension_name}: {d.coverage_pct}% "
            f"({d.pass_count}/{d.sensor_count} sensors)"
        )
        if d.missing_sensors:
            lines.append(f"    missing: {', '.join(d.missing_sensors)}")
        if d.redundant_sensors:
            lines.append(f"    redundant: {', '.join(d.redundant_sensors)}")

    if report.blind_spots:
        lines.extend(["", "Blind spots:"])
        for spot in report.blind_spots:
            lines.append(f"  - {spot}")

    if report.improvement_plan:
        lines.extend(["", "Improvement plan:"])
        for i, item in enumerate(report.improvement_plan, 1):
            lines.append(f"  {i}. {item}")

    if report.baseline_comparison:
        lines.extend(["", "Baseline comparison:"])
        trend = report.baseline_comparison.get("trend", "unknown")
        delta = report.baseline_comparison.get("maturity_delta", 0)
        lines.append(f"  Trend: {trend} (maturity delta: {delta:+d})")

    lines.extend(["", "Safety notes:"])
    for note in report.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"
