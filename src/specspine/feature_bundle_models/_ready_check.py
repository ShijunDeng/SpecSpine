from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "FeatureReadyCheck",
]


@dataclass(frozen=True)
class FeatureReadyCheck:
    id: str
    status: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "message": self.message,
            "status": self.status,
        }
