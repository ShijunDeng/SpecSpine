from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "ImpactEntry",
    "ImpactResult",
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
