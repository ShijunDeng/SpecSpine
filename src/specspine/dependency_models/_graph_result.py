from __future__ import annotations

from dataclasses import dataclass, field

from ._edges import DependencyEdge
from ._node import DependencyNode

__all__ = [
    "DependencyGraphResult",
]


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
