from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DependencyNode",
]


@dataclass(frozen=True)
class DependencyNode:
    slug: str
    effort: str
    milestone: str
    dep_count: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "dep_count": self.dep_count,
            "effort": self.effort,
            "milestone": self.milestone,
            "slug": self.slug,
        }
