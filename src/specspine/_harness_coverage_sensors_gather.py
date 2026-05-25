from __future__ import annotations

from pathlib import Path

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
)
from .harness import HarnessFeedbackSensor

__all__ = [
    "_gather_sensors_by_name",
]


def _gather_sensors_by_name(
    slug: str, resolved_root: Path
) -> dict[str, list[HarnessFeedbackSensor]]:
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
    return all_sensors_by_name
