from __future__ import annotations

__all__ = [
    "_topological_sort",
    "topological_sort",
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
