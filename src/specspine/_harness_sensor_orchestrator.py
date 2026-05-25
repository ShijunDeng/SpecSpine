from __future__ import annotations

from pathlib import Path

from .features import validate_feature_slug
from .harness_computational import _run_computational_sensors
from .harness_inferential import _run_inferential_sensors

__all__ = [
    "collect_harness_sensors",
    "compute_sensor_status",
]


def collect_harness_sensors(
    feature_id: str,
    resolved_root: Path,
) -> list:
    computational_sensors = _run_computational_sensors(feature_id, resolved_root)
    inferential_sensors = _run_inferential_sensors(feature_id, resolved_root)
    return computational_sensors + inferential_sensors


def compute_sensor_status(all_sensors: list) -> tuple[str, dict]:
    total_sensors = len(all_sensors)
    pass_sensors = sum(1 for s in all_sensors if s.status == "pass")
    fail_sensors = sum(1 for s in all_sensors if s.status == "fail")
    warn_sensors = sum(1 for s in all_sensors if s.status == "warn")

    if fail_sensors == 0 and warn_sensors == 0:
        overall_status = "healthy"
    elif fail_sensors == 0:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    steering_summary = {
        "fail_sensors": fail_sensors,
        "pass_sensors": pass_sensors,
        "total_sensors": total_sensors,
        "warn_sensors": warn_sensors,
    }

    return overall_status, steering_summary
