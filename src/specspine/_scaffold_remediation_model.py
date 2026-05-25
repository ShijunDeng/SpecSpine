from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScaffoldRemediationStep:
    ac_id: str
    action: str
    target_path: str
    class_name: str
    method_name: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "action": self.action,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "target_path": self.target_path,
        }


__all__ = [
    "ScaffoldRemediationStep",
]
