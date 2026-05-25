from __future__ import annotations

from pathlib import Path

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    list_feature_bundles,
)
from .harness import (
    HarnessFeedbackSensor,
    build_harness_quality,
)

from .harness_coverage_models import DIMENSION_SENSOR_MAP

__all__ = [
    "_collect_sensors_for_feature",
]


def _collect_sensors_for_feature(root: Path, slug: str) -> list[HarnessFeedbackSensor]:
    resolved_root = root.expanduser().resolve()
    try:
        quality_report = build_harness_quality(resolved_root, slug)
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        return []

    sensors: list[HarnessFeedbackSensor] = []
    sensor_by_dimension: dict[str, list[HarnessFeedbackSensor]] = {
        "verification": [],
        "coverage": [],
        "grading": [],
        "validation": [],
        "consistency": [],
        "hygiene": [],
        "security": [],
        "change_risk": [],
    }

    all_sensors_by_name: dict[str, list[HarnessFeedbackSensor]] = {}

    bundles = list_feature_bundles(resolved_root)
    feature_bundles = [b for b in bundles if b.get("slug") == slug]
    if feature_bundles:
        try:
            from .harness import _run_computational_sensors, _run_inferential_sensors
            computational = _run_computational_sensors(slug, resolved_root)
            inferential = _run_inferential_sensors(slug, resolved_root)
            all_s = computational + inferential
            for s in all_s:
                all_sensors_by_name.setdefault(s.name, []).append(s)
        except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
            pass

    for dim, sensor_name in DIMENSION_SENSOR_MAP.items():
        dim_sensors = all_sensors_by_name.get(sensor_name, [])
        sensor_by_dimension[dim] = dim_sensors

    for dim, dim_sensors in sensor_by_dimension.items():
        sensors.extend(dim_sensors)

    return sensors
