from __future__ import annotations

from .harness_models import HarnessFeedbackReport

__all__ = [
    "_collect_failing_ac_ids",
]


def _collect_failing_ac_ids(feedback_report: HarnessFeedbackReport) -> set[str]:
    all_failing_ac_ids: set[str] = set()
    for sensor in feedback_report.sensors:
        for ac_id in sensor.ac_ids:
            if ac_id and sensor.status == "fail":
                all_failing_ac_ids.add(ac_id)
    return all_failing_ac_ids
