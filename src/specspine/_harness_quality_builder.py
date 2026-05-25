from __future__ import annotations

from pathlib import Path

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)
from .harness_computational import _run_computational_sensors
from .harness_inferential import _run_inferential_sensors
from .harness_models import HarnessQualityReport

__all__ = [
    "build_harness_quality",
]


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

    sensors = []
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

    dimension_scores = {}
    sensor_by_dimension = {
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
