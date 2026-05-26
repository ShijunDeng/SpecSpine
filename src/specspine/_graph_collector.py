from __future__ import annotations

from pathlib import Path

from .dependency_build_extract import _list_feature_slugs
from .dependency_build_graph_nodes import _build_node_map
from .dependency_build_graph_edges import _build_adjacency

__all__ = [
    "_collect_graph_data",
]


def _collect_graph_data(
    resolved_root: Path,
    feature_slugs: list[str] | None,
) -> dict:
    all_slugs = _list_feature_slugs(resolved_root)
    if feature_slugs:
        valid_slugs = [s for s in feature_slugs if s in all_slugs]
    else:
        valid_slugs = list(all_slugs)

    node_map = _build_node_map(resolved_root, valid_slugs)

    adj, explicit_edges = _build_adjacency(resolved_root, valid_slugs)

    for slug in valid_slugs:
        node_map[slug]["dep_count"] = len(adj[slug])

    return {
        "valid_slugs": valid_slugs,
        "node_map": node_map,
        "adj": adj,
        "explicit_edges": explicit_edges,
    }
