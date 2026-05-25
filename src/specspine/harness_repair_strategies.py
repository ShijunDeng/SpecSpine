from __future__ import annotations

import json
from typing import Any

from .harness_models import HarnessFeedbackReport, HarnessFeedbackSensor, RepairStrategy

__all__ = [
    "_classify_root_causes",
    "_collect_gaps_from_sensors",
    "_generate_repair_strategies",
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
