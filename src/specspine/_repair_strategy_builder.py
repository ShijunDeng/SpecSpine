from __future__ import annotations

import json

from .harness_models import HarnessFeedbackReport, RepairStrategy

__all__ = [
    "_build_ac_repair_strategy",
]


def _build_ac_repair_strategy(
    ac_id: str,
    feedback_report: HarnessFeedbackReport,
) -> RepairStrategy:
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

    return RepairStrategy(
        ac_id=ac_id,
        target_file=target_file,
        edit_description=edit_description,
        verification_command=verification_command,
        success_criteria=success_criteria,
    )
