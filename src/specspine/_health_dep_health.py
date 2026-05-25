from __future__ import annotations

from pathlib import Path

from .dependency import build_dependency_graph
from .health_models import DependencyHealth

__all__ = [
    "_build_dependency_health",
]


def _build_dependency_health(root: Path) -> DependencyHealth:
    try:
        graph = build_dependency_graph(root)
    except OSError:
        return DependencyHealth(
            features_total=0,
            cycles=[],
            critical_path=[],
            critical_path_effort=0,
        )

    nodes = graph.get("nodes", [])
    critical = graph.get("critical_path", {})
    return DependencyHealth(
        features_total=len(nodes),
        cycles=graph.get("cycles", []),
        critical_path=critical.get("path", []),
        critical_path_effort=int(critical.get("total_effort", 0)),
    )
