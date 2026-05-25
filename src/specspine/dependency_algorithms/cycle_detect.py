from __future__ import annotations

__all__ = [
    "_detect_cycles",
    "detect_cycles",
]


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
