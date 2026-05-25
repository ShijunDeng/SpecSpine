from __future__ import annotations

import re
from dataclasses import dataclass, field

__all__ = [
    "EFFORT_VALUES",
    "DEFAULT_EFFORT",
    "EXPLICIT_DEP_PATTERNS",
    "_resolve_effort",
    "DependencyEdge",
    "DependencyNode",
    "DependencyGraphResult",
]

EFFORT_VALUES = {"S": 1, "M": 2, "L": 4, "XL": 8}
DEFAULT_EFFORT = 3


def _resolve_effort(effort: str) -> int:
    return EFFORT_VALUES.get(effort, DEFAULT_EFFORT)

EXPLICIT_DEP_PATTERNS = [
    re.compile(r"Feature\s+ID:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"depends\s+on\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"after\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"blocked\s+by\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"requires\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"prerequisite:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
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


@dataclass(frozen=True)
class DependencyGraphResult:
    root: str
    feature_filter: str | None
    nodes: list[DependencyNode]
    edges: list[DependencyEdge]
    topological_order: list[str] | None
    cycles: list[list[str]]
    critical_path: dict[str, object]
    recommended_commands: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "critical_path": self.critical_path,
            "cycles": self.cycles,
            "edges": [edge.as_dict() for edge in self.edges],
            "feature_filter": self.feature_filter,
            "nodes": [node.as_dict() for node in self.nodes],
            "recommended_commands": self.recommended_commands,
            "root": self.root,
            "topological_order": self.topological_order,
        }
