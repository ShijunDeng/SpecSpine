from __future__ import annotations

import re
from dataclasses import dataclass

FEATURE_ID_RE = re.compile(r"Feature\s+ID:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
DEPENDENCY_PATTERNS = [
    re.compile(r"depends\s+on\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"after\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"blocked\s+by\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"requires\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
]


@dataclass(frozen=True)
class ImpactEntry:
    change_id: str
    affected_type: str
    affected_id: str
    severity: str

    def as_dict(self) -> dict[str, str]:
        return {
            "affected_id": self.affected_id,
            "affected_type": self.affected_type,
            "change_id": self.change_id,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ImpactResult:
    slug: str
    impacts: list[ImpactEntry]

    @property
    def summary(self) -> dict[str, int]:
        return {
            "breaking": sum(1 for i in self.impacts if i.severity == "breaking"),
            "info": sum(1 for i in self.impacts if i.severity == "info"),
            "total": len(self.impacts),
            "warning": sum(1 for i in self.impacts if i.severity == "warning"),
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "impacts": [i.as_dict() for i in self.impacts],
            "slug": self.slug,
            "summary": self.summary,
        }


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


__all__ = [
    "DEPENDENCY_PATTERNS",
    "FEATURE_ID_RE",
    "ImpactEntry",
    "ImpactResult",
    "RemediationAction",
]
