from __future__ import annotations

__all__ = [
    "_topological_sort",
    "_detect_cycles",
    "_compute_critical_path",
    "topological_sort",
    "detect_cycles",
    "compute_critical_path",
]


def _topological_sort(
    slugs: list[str],
    adj: dict[str, set[str]],
) -> list[str] | None:
    if not slugs:
        return []

    in_degree: dict[str, int] = {s: 0 for s in slugs}
    for slug in slugs:
        for dep in adj[slug]:
            if dep in in_degree:
                in_degree[dep] = in_degree.get(dep, 0) + 1

    queue: list[str] = sorted([s for s in slugs if in_degree[s] == 0])
    order: list[str] = []

    while queue:
        node = queue.pop(0)
        order.append(node)
        for dep in sorted(adj[node]):
            if dep in in_degree:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
                    queue.sort()

    if len(order) != len(slugs):
        return None

    return order


def _detect_cycles(
    slugs: list[str],
    adj: dict[str, set[str]],
) -> list[list[str]]:
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {s: WHITE for s in slugs}
    path: list[str] = []
    cycles: list[list[str]] = []

    def dfs(node: str) -> None:
        color[node] = GRAY
        path.append(node)
        for neighbor in sorted(adj[node]):
            if neighbor not in color:
                continue
            if color[neighbor] == GRAY:
                idx = path.index(neighbor)
                cycle = list(path[idx:]) + [neighbor]
                cycles.append(cycle)
            elif color[neighbor] == WHITE:
                dfs(neighbor)
        path.pop()
        color[node] = BLACK

    for slug in sorted(slugs):
        if color[slug] == WHITE:
            dfs(slug)

    return cycles


def _compute_critical_path(
    node_map: dict[str, dict[str, object]],
    adj: dict[str, set[str]],
    topo_order: list[str],
) -> dict[str, object]:
    from .dependency_models import _resolve_effort

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


def topological_sort(
    nodes: list[dict[str, object]],
    edges: list[dict[str, str]],
) -> list[str] | None:
    slugs = [n["slug"] for n in nodes]
    if not slugs:
        return []
    adj: dict[str, set[str]] = {s: set() for s in slugs}
    for edge in edges:
        from_slug = edge["from"]
        to_slug = edge["to"]
        if from_slug in adj and to_slug in slugs:
            adj[from_slug].add(to_slug)
    return _topological_sort(slugs, adj)


def detect_cycles(
    nodes: list[dict[str, object]],
    edges: list[dict[str, str]],
) -> list[list[str]]:
    slugs = [n["slug"] for n in nodes]
    if not slugs:
        return []
    adj: dict[str, set[str]] = {s: set() for s in slugs}
    for edge in edges:
        from_slug = edge["from"]
        to_slug = edge["to"]
        if from_slug in adj and to_slug in slugs:
            adj[from_slug].add(to_slug)
    return _detect_cycles(slugs, adj)


def compute_critical_path(
    nodes: list[dict[str, object]],
    edges: list[dict[str, str]],
    topo_order: list[str],
) -> dict[str, object]:
    from .dependency_models import _resolve_effort

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
