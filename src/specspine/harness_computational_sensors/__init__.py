from __future__ import annotations

from pathlib import Path

from ..harness_computational_readers import _extract_ac_ids, _read_feature_contents
from ..harness_models import HarnessFeedbackSensor
from ._sensors_coverage import _build_coverage_debt_sensor
from ._sensors_quality import _build_grading_rubric_sensor, _build_validation_contract_sensor
from ._sensors_verification import _build_verification_matrix_sensor

__all__ = [
    "_run_computational_sensors",
]


def _run_computational_sensors(slug: str, root) -> list[HarnessFeedbackSensor]:
    resolved_root = Path(root).expanduser().resolve()
    sensors: list[HarnessFeedbackSensor] = []

    contents = _read_feature_contents(resolved_root, slug)
    ac_ids = _extract_ac_ids(contents)

    sensors.append(_build_verification_matrix_sensor(resolved_root, slug, ac_ids))
    sensors.append(_build_coverage_debt_sensor(resolved_root, slug))
    sensors.append(_build_grading_rubric_sensor(resolved_root, slug))
    sensors.append(_build_validation_contract_sensor(resolved_root, slug))

    return sensors
