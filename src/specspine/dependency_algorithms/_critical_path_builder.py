from __future__ import annotations

from ._critical_path_core import _compute_critical_path

__all__ = [
    "compute_critical_path",
]


def compute_critical_path(
    nodes: list[dict[str, object]],
    edges: list[dict[str, str]],
    topo_order: list[str],
) -> dict[str, object]:
    from ..dependency_models import _resolve_effort

    if not topo_order:
        return {"path": [], "total_effort": 0}
    node_map: dict[str, dict[str, object]] = {n["slug"]: n for n in nodes}
    adj: dict[str, set[str]] = {n["slug"]: set() for n in nodes}
    for edge in edges:
        from_slug = edge["from"]
        to_slug = edge["to"]
        if from_slug in adj and to_slug in node_map:
            adj[from_slug].add(to_slug)
    return _compute_critical_path(node_map, adj, topo_order)
