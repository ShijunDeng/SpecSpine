from __future__ import annotations

import json

from .harness_models import HarnessFeedbackReport, HarnessQualityReport

__all__ = [
    "render_harness_feedback_json",
    "render_harness_feedback_text",
    "render_harness_quality_json",
    "render_harness_quality_text",
]


def render_harness_feedback_json(report: HarnessFeedbackReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_harness_feedback_text(report: HarnessFeedbackReport) -> str:
    lines = [
        f"Harness feedback: {report.feature_id}",
        f"Status: {report.status}",
        "",
        "Sensors:",
    ]
    for sensor in report.sensors:
        ac_info = f" ac_ids={','.join(sensor.ac_ids)}" if sensor.ac_ids else ""
        lines.append(
            f"  - [{sensor.status}] {sensor.sensor_type}/{sensor.name}{ac_info}"
        )

    lines.extend(["", "Repair strategies:"])
    if report.repair_strategies:
        for strategy in report.repair_strategies:
            lines.append(
                f"  - {strategy.ac_id}: {strategy.edit_description}"
            )
            lines.append(f"    target: {strategy.target_file}")
            lines.append(f"    verify: {strategy.verification_command}")
            lines.append(f"    success: {strategy.success_criteria}")
    else:
        lines.append("- None.")

    lines.extend(["", "Root causes:"])
    for category, items in report.root_causes.items():
        if items:
            lines.append(f"  - {category}: {len(items)} item(s)")
        else:
            lines.append(f"  - {category}: none")

    lines.extend(["", f"Steering: pass={report.steering_summary.get('pass_sensors', 0)} "
                      f"fail={report.steering_summary.get('fail_sensors', 0)} "
                      f"warn={report.steering_summary.get('warn_sensors', 0)} "
                      f"total={report.steering_summary.get('total_sensors', 0)}"])

    if report.harness_quality:
        lines.extend([
            "",
            f"Harness quality: {report.harness_quality.harness_coverage_pct}% coverage",
        ])

    lines.extend(["", "Safety notes:"])
    for note in report.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"


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
