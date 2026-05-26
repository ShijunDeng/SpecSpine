from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DependencyEdge",
]


@dataclass(frozen=True)
class DependencyEdge:
    from_slug: str
    to_slug: str
    reason: str
    inference: str

    def as_dict(self) -> dict[str, str]:
        return {
            "from": self.from_slug,
            "inference": self.inference,
            "reason": self.reason,
            "to": self.to_slug,
        }
