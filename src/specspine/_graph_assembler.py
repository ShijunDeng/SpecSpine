from __future__ import annotations

from .dependency_models import DependencyGraphResult
from .dependency_build_graph_nodes import _build_nodes
from .dependency_graph_recommendations import _assemble_recommendations

__all__ = [
    "_assemble_graph_result",
]


def _assemble_graph_result(
    resolved_root,
    feature_slugs: list[str] | None,
    valid_slugs: list[str],
    node_map: dict,
    explicit_edges: list,
    topo_order,
    cycles: list,
    critical: dict,
) -> dict:
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
