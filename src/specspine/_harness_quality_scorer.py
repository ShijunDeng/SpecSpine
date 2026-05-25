from __future__ import annotations

from .harness_models import HarnessFeedbackSensor

__all__ = [
    "HARNESS_DIMENSIONS",
    "_compute_harness_coverage",
    "_compute_dimension_scores",
]

HARNESS_DIMENSIONS = (
    "verification",
    "coverage",
    "grading",
    "validation",
    "consistency",
    "hygiene",
    "security",
    "change_risk",
)

_DIMENSION_SENSOR_MAP = {
    "verification": "verification_matrix",
    "coverage": "coverage_debt",
    "grading": "grading_rubric",
    "validation": "validation_contract",
    "consistency": "consistency_scan",
    "hygiene": "hygiene_scan",
    "security": "security_cues",
    "change_risk": "change_risk",
}


def _compute_harness_coverage(sensors: list[HarnessFeedbackSensor]) -> float:
    sensor_count = len(sensors)
    pass_count = sum(1 for s in sensors if s.status == "pass")
    return (pass_count / sensor_count * 100) if sensor_count > 0 else 0.0


def _compute_dimension_scores(sensors: list[HarnessFeedbackSensor]) -> dict[str, float]:
    dimension_scores: dict[str, float] = {}
    for dimension, sensor_name in _DIMENSION_SENSOR_MAP.items():
        dim_sensors = [s for s in sensors if s.name == sensor_name]
        if not dim_sensors:
            dimension_scores[dimension] = 0.0
        else:
            dim_pass = sum(1 for s in dim_sensors if s.status == "pass")
            dimension_scores[dimension] = (dim_pass / len(dim_sensors)) * 100
    return dimension_scores
