from __future__ import annotations

import json

from .harness_models import HarnessFeedbackReport, RepairStrategy

__all__ = [
    "_add_computational_fallback_strategies",
]


def _add_computational_fallback_strategies(
    feedback_report: HarnessFeedbackReport,
    strategies: list[RepairStrategy],
) -> None:
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
