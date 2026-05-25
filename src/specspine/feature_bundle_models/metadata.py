from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "FeatureMetadata",
]


@dataclass(frozen=True)
class FeatureMetadata:
    priority: str
    owner: str
    milestone: str
    target_release: str
    project: str
    effort: str

    def as_dict(self) -> dict[str, str]:
        return {
            "effort": self.effort,
            "milestone": self.milestone,
            "owner": self.owner,
            "priority": self.priority,
            "project": self.project,
            "target_release": self.target_release,
        }
