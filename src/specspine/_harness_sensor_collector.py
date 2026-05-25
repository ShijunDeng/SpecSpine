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
from .harness_models import HarnessFeedbackSensor

__all__ = [
    "_collect_sensors_for_feature",
    "_collect_sensors_for_workspace",
]


def _collect_sensors_for_feature(
    feature_id: str,
    resolved_root: Path,
) -> list[HarnessFeedbackSensor]:
    try:
        computational = _run_computational_sensors(feature_id, resolved_root)
        inferential = _run_inferential_sensors(feature_id, resolved_root)
        return computational + inferential
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        return []


def _collect_sensors_for_workspace(resolved_root: Path) -> list[HarnessFeedbackSensor]:
    sensors: list[HarnessFeedbackSensor] = []
    bundles = list_feature_bundles(resolved_root)
    for bundle in bundles:
        slug = str(bundle["slug"])
        try:
            computational = _run_computational_sensors(slug, resolved_root)
            inferential = _run_inferential_sensors(slug, resolved_root)
            sensors.extend(computational + inferential)
        except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
            continue
    return sensors
