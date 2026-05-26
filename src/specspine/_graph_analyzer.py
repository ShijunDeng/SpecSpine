from __future__ import annotations

from .dependency_algorithms import (
    _compute_critical_path,
    _detect_cycles,
    _topological_sort,
)

__all__ = [
    "_analyze_graph_structure",
]


def _analyze_graph_structure(
    valid_slugs: list[str],
    adj: dict,
    node_map: dict,
) -> dict:
    topo_order = _topological_sort(valid_slugs, adj)
    cycles = _detect_cycles(valid_slugs, adj)

    if topo_order is not None and valid_slugs:
        critical = _compute_critical_path(node_map, adj, topo_order)
    else:
        critical = {"path": [], "total_effort": 0}

    return {
        "topo_order": topo_order,
        "cycles": cycles,
        "critical": critical,
    }
