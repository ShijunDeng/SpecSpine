from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "HarnessFeedbackSensor",
]


@dataclass(frozen=True)
class HarnessFeedbackSensor:
    sensor_type: str
    name: str
    status: str
    output: dict[str, Any]
    ac_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "ac_ids": list(self.ac_ids),
            "name": self.name,
            "output": dict(self.output),
            "sensor_type": self.sensor_type,
            "status": self.status,
        }
