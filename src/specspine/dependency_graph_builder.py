from __future__ import annotations

from pathlib import Path

from .dependency_algorithms import (
    _compute_critical_path,
    _detect_cycles,
    _topological_sort,
)
from .dependency_models import DependencyGraphResult
from .dependency_build_extract import _list_feature_slugs
from .dependency_build_graph_nodes import _build_node_map, _build_nodes
from .dependency_build_graph_edges import _build_adjacency
from .dependency_graph_recommendations import _assemble_recommendations

__all__ = [
    "build_dependency_graph",
]


def build_dependency_graph(
    root: Path,
    feature_slugs: list[str] | None = None,
) -> dict[str, object]:
    resolved_root = root.expanduser().resolve()

    all_slugs = _list_feature_slugs(resolved_root)
    if feature_slugs:
        valid_slugs = [s for s in feature_slugs if s in all_slugs]
    else:
        valid_slugs = list(all_slugs)

    node_map = _build_node_map(resolved_root, valid_slugs)

    adj, explicit_edges = _build_adjacency(resolved_root, valid_slugs)

    for slug in valid_slugs:
        node_map[slug]["dep_count"] = len(adj[slug])

    topo_order = _topological_sort(valid_slugs, adj)
    cycles = _detect_cycles(valid_slugs, adj)

    if topo_order is not None and valid_slugs:
        critical = _compute_critical_path(node_map, adj, topo_order)
    else:
        critical = {"path": [], "total_effort": 0}

    nodes = _build_nodes(node_map, valid_slugs)
    edges = explicit_edges

    filter_desc = feature_slugs[0] if feature_slugs and len(feature_slugs) == 1 else None

    recommended = _assemble_recommendations(cycles, topo_order, critical, valid_slugs)

    result = DependencyGraphResult(
        root=str(resolved_root),
        feature_filter=filter_desc,
        nodes=nodes,
        edges=edges,
        topological_order=topo_order if valid_slugs else None,
        cycles=cycles,
        critical_path=critical,
        recommended_commands=recommended,
    )

    return result.as_dict()
