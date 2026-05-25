from __future__ import annotations

from ._sensors_consistency import _build_consistency_sensor
from ._sensors_quality import _build_hygiene_sensor, _build_security_sensor
from ._sensors_risk import _build_change_risk_sensor
from ..harness_models import HarnessFeedbackSensor

__all__ = [
    "_run_inferential_sensors",
]


def _run_inferential_sensors(slug: str, root) -> list[HarnessFeedbackSensor]:
    from pathlib import Path

    resolved_root = root.expanduser().resolve() if isinstance(root, Path) else Path(root).expanduser().resolve()
    sensors: list[HarnessFeedbackSensor] = []
    sensors.append(_build_consistency_sensor(slug, resolved_root))
    sensors.append(_build_hygiene_sensor(resolved_root))
    sensors.append(_build_security_sensor(slug, resolved_root))
    sensors.append(_build_change_risk_sensor(slug, resolved_root))
    return sensors
