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

from .harness_coverage_models import (
    DIMENSION_SENSOR_MAP,
    GOVERNED_DIMENSIONS,
    HarnessDimensionCoverage,
)

__all__ = [
    "_collect_sensors_for_feature",
    "_evaluate_dimensions",
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


def _evaluate_dimensions(slug: str, root: Path) -> list[HarnessDimensionCoverage]:
    resolved_root = root.expanduser().resolve()
    dimensions: list[HarnessDimensionCoverage] = []

    all_sensors_by_name: dict[str, list[HarnessFeedbackSensor]] = {}
    try:
        from .harness import _run_computational_sensors, _run_inferential_sensors
        computational = _run_computational_sensors(slug, resolved_root)
        inferential = _run_inferential_sensors(slug, resolved_root)
        all_s = computational + inferential
        for s in all_s:
            all_sensors_by_name.setdefault(s.name, []).append(s)
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        pass

    for dim in GOVERNED_DIMENSIONS:
        sensor_name = DIMENSION_SENSOR_MAP[dim]
        dim_sensors = all_sensors_by_name.get(sensor_name, [])
        sensor_count = len(dim_sensors)
        pass_count = sum(1 for s in dim_sensors if s.status == "pass")
        coverage_pct = (pass_count / sensor_count * 100) if sensor_count > 0 else 0.0

        missing_sensors: tuple[str, ...] = ()
        if sensor_count == 0:
            missing_sensors = (sensor_name,)

        redundant: list[str] = []
        if sensor_count > 1:
            ac_sets = [frozenset(s.ac_ids) for s in dim_sensors]
            for i in range(len(dim_sensors)):
                for j in range(i + 1, len(dim_sensors)):
                    if ac_sets[i] & ac_sets[j]:
                        redundant.append(dim_sensors[i].name)
                        redundant.append(dim_sensors[j].name)
            redundant_sensors = tuple(sorted(set(redundant)))
        else:
            redundant_sensors = ()

        dimensions.append(
            HarnessDimensionCoverage(
                dimension_name=dim,
                sensor_count=sensor_count,
                pass_count=pass_count,
                coverage_pct=round(coverage_pct, 2),
                missing_sensors=missing_sensors,
                redundant_sensors=redundant_sensors,
            )
        )

    return dimensions
