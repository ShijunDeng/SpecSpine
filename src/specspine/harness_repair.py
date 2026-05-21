from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)
from .harness_computational import _run_computational_sensors
from .harness_inferential import _run_inferential_sensors
from .harness_models import HarnessFeedbackReport, HarnessFeedbackSensor, HarnessQualityReport, RepairStrategy

__all__ = [
    "_classify_root_causes",
    "_collect_gaps_from_sensors",
    "_generate_repair_strategies",
    "build_harness_feedback",
    "build_harness_quality",
    "render_harness_feedback_json",
    "render_harness_feedback_text",
    "render_harness_quality_json",
    "render_harness_quality_text",
]


def _generate_repair_strategies(feedback_report: HarnessFeedbackReport) -> list[RepairStrategy]:
    strategies: list[RepairStrategy] = []
    seen_ac_ids: set[str] = set()

    all_failing_ac_ids: set[str] = set()
    for sensor in feedback_report.sensors:
        for ac_id in sensor.ac_ids:
            if ac_id and sensor.status == "fail":
                all_failing_ac_ids.add(ac_id)

    for ac_id in sorted(all_failing_ac_ids):
        if ac_id in seen_ac_ids:
            continue
        seen_ac_ids.add(ac_id)

        sensor_names = [
            sensor.name
            for sensor in feedback_report.sensors
            if ac_id in sensor.ac_ids and sensor.status == "fail"
        ]

        target_file = f"specs/features/{feedback_report.feature_id}.md"
        if "coverage_debt" in sensor_names or "grading_rubric" in sensor_names:
            target_file = f"quality/features/{feedback_report.feature_id}.md"

        edit_description = (
            f"Address acceptance criterion {ac_id} failures detected by: "
            f"{', '.join(sorted(sensor_names))}."
        )

        verification_command = (
            f"specspine verify matrix {feedback_report.feature_id} . --json"
        )

        success_criteria = (
            f"AC {ac_id} must pass verification matrix, coverage debt, and grading rubric checks."
        )

        strategies.append(
            RepairStrategy(
                ac_id=ac_id,
                target_file=target_file,
                edit_description=edit_description,
                verification_command=verification_command,
                success_criteria=success_criteria,
            )
        )

    if not strategies:
        computational_failures = [
            s for s in feedback_report.sensors
            if s.sensor_type == "computational" and s.status == "fail"
        ]
        for sensor in sorted(computational_failures, key=lambda s: s.name):
            if sensor.name not in [s.name for s in [r for r in []]]:
                strategies.append(
                    RepairStrategy(
                        ac_id="SENSOR_FAILURE",
                        target_file=f"specs/features/{feedback_report.feature_id}.md",
                        edit_description=f"Fix {sensor.name} sensor failure: {json.dumps(sensor.output)}",
                        verification_command=f"specspine harness feedback {feedback_report.feature_id} . --json",
                        success_criteria=f"{sensor.name} sensor must return pass status.",
                    )
                )

    return strategies


def _classify_root_causes(gaps: list[dict[str, str]]) -> dict[str, Any]:
    categories: dict[str, list[dict[str, str]]] = {
        "missing_spec": [],
        "missing_code": [],
        "missing_test": [],
        "stale_coverage": [],
        "contract_violation": [],
    }

    for gap in gaps:
        gap_id = gap.get("id", "")
        gap_message = gap.get("message", "").lower()

        if any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("missing_file", "missing_spec", "spec")
        ):
            categories["missing_spec"].append(gap)
        elif any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("missing_code", "implementation", "not_implemented")
        ):
            categories["missing_code"].append(gap)
        elif any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("missing_test", "test_coverage", "coverage", "no test")
        ):
            categories["missing_test"].append(gap)
        elif any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("stale", "outdated", "unknown_acceptance")
        ):
            categories["stale_coverage"].append(gap)
        else:
            categories["contract_violation"].append(gap)

    return {
        category: items
        for category, items in categories.items()
    }


def _collect_gaps_from_sensors(sensors: list[HarnessFeedbackSensor]) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    for sensor in sensors:
        if sensor.status == "fail":
            gaps.append(
                {
                    "id": f"sensor:{sensor.name}",
                    "message": f"Sensor {sensor.name} returned status: {sensor.status}",
                    "sensor_type": sensor.sensor_type,
                }
            )
        for ac_id in sensor.ac_ids:
            gaps.append(
                {
                    "id": ac_id,
                    "message": f"AC {ac_id} flagged by sensor {sensor.name}",
                    "sensor_type": sensor.sensor_type,
                }
            )
    return gaps


def build_harness_feedback(slug: str, root: Path) -> HarnessFeedbackReport:
    feature_id = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    computational_sensors = _run_computational_sensors(feature_id, resolved_root)
    inferential_sensors = _run_inferential_sensors(feature_id, resolved_root)
    all_sensors = computational_sensors + inferential_sensors

    gaps = _collect_gaps_from_sensors(all_sensors)
    root_causes = _classify_root_causes(gaps)

    feedback_report = HarnessFeedbackReport(
        feature_id=feature_id,
        status="unknown",
        sensors=tuple(all_sensors),
        repair_strategies=(),
        root_causes=root_causes,
        steering_summary={},
        harness_quality=None,
        safety_notes=(),
    )

    repair_strategies = _generate_repair_strategies(feedback_report)

    total_sensors = len(all_sensors)
    pass_sensors = sum(1 for s in all_sensors if s.status == "pass")
    fail_sensors = sum(1 for s in all_sensors if s.status == "fail")
    warn_sensors = sum(1 for s in all_sensors if s.status == "warn")

    if fail_sensors == 0 and warn_sensors == 0:
        overall_status = "healthy"
    elif fail_sensors == 0:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    steering_summary = {
        "fail_sensors": fail_sensors,
        "pass_sensors": pass_sensors,
        "repair_strategies_count": len(repair_strategies),
        "total_sensors": total_sensors,
        "warn_sensors": warn_sensors,
    }

    harness_quality = build_harness_quality(resolved_root, feature_id)

    safety_notes = (
        "This harness feedback report is advisory local evidence.",
        "Recommended commands are advisory and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )

    return HarnessFeedbackReport(
        feature_id=feature_id,
        status=overall_status,
        sensors=tuple(all_sensors),
        repair_strategies=tuple(repair_strategies),
        root_causes=root_causes,
        steering_summary=steering_summary,
        harness_quality=harness_quality,
        safety_notes=safety_notes,
    )


def build_harness_quality(root: Path, feature_id: str = "") -> HarnessQualityReport:
    resolved_root = root.expanduser().resolve()
    dimensions = (
        "verification",
        "coverage",
        "grading",
        "validation",
        "consistency",
        "hygiene",
        "security",
        "change_risk",
    )

    sensors: list[HarnessFeedbackSensor] = []
    if feature_id:
        try:
            computational = _run_computational_sensors(feature_id, resolved_root)
            inferential = _run_inferential_sensors(feature_id, resolved_root)
            sensors = computational + inferential
        except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
            sensors = []
    else:
        bundles = list_feature_bundles(resolved_root)
        for bundle in bundles:
            slug = str(bundle["slug"])
            try:
                computational = _run_computational_sensors(slug, resolved_root)
                inferential = _run_inferential_sensors(slug, resolved_root)
                sensors.extend(computational + inferential)
            except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
                continue

    sensor_count = len(sensors)
    pass_count = sum(1 for s in sensors if s.status == "pass")
    harness_coverage_pct = (pass_count / sensor_count * 100) if sensor_count > 0 else 0.0

    dimension_scores: dict[str, float] = {}
    sensor_by_dimension: dict[str, list[HarnessFeedbackSensor]] = {
        "verification": [s for s in sensors if s.name == "verification_matrix"],
        "coverage": [s for s in sensors if s.name == "coverage_debt"],
        "grading": [s for s in sensors if s.name == "grading_rubric"],
        "validation": [s for s in sensors if s.name == "validation_contract"],
        "consistency": [s for s in sensors if s.name == "consistency_scan"],
        "hygiene": [s for s in sensors if s.name == "hygiene_scan"],
        "security": [s for s in sensors if s.name == "security_cues"],
        "change_risk": [s for s in sensors if s.name == "change_risk"],
    }

    for dimension, dim_sensors in sensor_by_dimension.items():
        if not dim_sensors:
            dimension_scores[dimension] = 0.0
        else:
            dim_pass = sum(1 for s in dim_sensors if s.status == "pass")
            dimension_scores[dimension] = (dim_pass / len(dim_sensors)) * 100

    resolved_feature_id = feature_id if feature_id else "workspace"

    return HarnessQualityReport(
        feature_id=resolved_feature_id,
        governed_dimensions=dimensions,
        sensor_count=sensor_count,
        harness_coverage_pct=harness_coverage_pct,
        dimension_scores=dimension_scores,
    )


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
