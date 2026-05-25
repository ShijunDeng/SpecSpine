from __future__ import annotations

__all__ = [
    "_compute_critical_path",
    "compute_critical_path",
]


def _compute_critical_path(
    node_map: dict[str, dict[str, object]],
    adj: dict[str, set[str]],
    topo_order: list[str],
) -> dict[str, object]:
    from ..dependency_models import _resolve_effort

    if not topo_order:
        return {"path": [], "total_effort": 0}

    dist: dict[str, int] = {}
    prev: dict[str, str | None] = {}
    for slug in topo_order:
        dist[slug] = _resolve_effort(node_map[slug]["effort"])
        prev[slug] = None

    for slug in topo_order:
        for dep in sorted(adj[slug]):
            if dep in dist:
                new_dist = dist[slug] + _resolve_effort(node_map[dep]["effort"])
                if new_dist > dist[dep]:
                    dist[dep] = new_dist
                    prev[dep] = slug

    if not dist:
        return {"path": [], "total_effort": 0}

    end_slug = max(dist, key=lambda s: dist[s])
    path: list[str] = []
    current: str | None = end_slug
    while current is not None:
        path.append(current)
        current = prev[current]

    path.reverse()
    total = sum(
        _resolve_effort(node_map[s]["effort"]) for s in path
    )

    return {"path": path, "total_effort": total}


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
