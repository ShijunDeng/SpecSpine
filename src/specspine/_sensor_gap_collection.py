from __future__ import annotations

from .harness_models import HarnessFeedbackSensor

__all__ = [
    "_collect_gaps_from_sensors",
]


def _collect_gaps_from_sensors(sensors: list[HarnessFeedbackSensor]) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    for sensor in sensors:
        if sensor.status == "fail":
            gaps.append(
                {
                    "id": f"sensor:{sensor.name}",
                    "message": f"Sensor {sensor.name} returned status: {sensor.status}",
                    "sensor_type": sensor.sensor_type,
                }
            )
        for ac_id in sensor.ac_ids:
            gaps.append(
                {
                    "id": ac_id,
                    "message": f"AC {ac_id} flagged by sensor {sensor.name}",
                    "sensor_type": sensor.sensor_type,
                }
            )
    return gaps
