from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "RemediationAction",
]


@dataclass(frozen=True)
class RemediationAction:
    action_id: str
    description: str
    priority: int
    target_file: str

    def as_dict(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "description": self.description,
            "priority": self.priority,
            "target_file": self.target_file,
        }
