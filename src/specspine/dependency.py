from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    FEATURE_DIRECTORIES,
    read_feature_metadata,
)

EFFORT_VALUES = {"S": 1, "M": 2, "L": 4, "XL": 8}
DEFAULT_EFFORT = 3

EXPLICIT_DEP_PATTERNS = [
    re.compile(r"Feature\s+ID:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"depends\s+on\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"after\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"blocked\s+by\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"requires\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"prerequisite:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
]


@dataclass(frozen=True)
class DependencyEdge:
    from_slug: str
    to_slug: str
    reason: str
    inference: str

    def as_dict(self) -> dict[str, str]:
        return {
            "from": self.from_slug,
            "inference": self.inference,
            "reason": self.reason,
            "to": self.to_slug,
        }


@dataclass(frozen=True)
class DependencyNode:
    slug: str
    effort: str
    milestone: str
    dep_count: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "dep_count": self.dep_count,
            "effort": self.effort,
            "milestone": self.milestone,
            "slug": self.slug,
        }


@dataclass(frozen=True)
class DependencyGraphResult:
    root: str
    feature_filter: str | None
    nodes: list[DependencyNode]
    edges: list[DependencyEdge]
    topological_order: list[str] | None
    cycles: list[list[str]]
    critical_path: dict[str, object]
    recommended_commands: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "critical_path": self.critical_path,
            "cycles": self.cycles,
            "edges": [edge.as_dict() for edge in self.edges],
            "feature_filter": self.feature_filter,
            "nodes": [node.as_dict() for node in self.nodes],
            "recommended_commands": self.recommended_commands,
            "root": self.root,
            "topological_order": self.topological_order,
        }


def _resolve_effort(effort: str) -> int:
    return EFFORT_VALUES.get(effort, DEFAULT_EFFORT)


def _extract_slugs_from_text(text: str, current_slug: str, valid_slugs: set[str] | None = None) -> list[str]:
    slugs: list[str] = []
    for pattern in EXPLICIT_DEP_PATTERNS:
        for match in pattern.finditer(text):
            found = match.group(1)
            if found != current_slug and found not in slugs:
                if valid_slugs is None or found in valid_slugs:
                    slugs.append(found)
    return slugs


def _list_feature_slugs(root: Path) -> list[str]:
    by_slug: dict[str, bool] = {}
    for directory_name in FEATURE_DIRECTORIES.values():
        directory = root / directory_name
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            by_slug[path.stem] = True
    return sorted(by_slug)


def _read_all_feature_content(root: Path, slug: str) -> str:
    parts: list[str] = []
    for kind in FEATURE_FILE_PATHS:
        file_path = root / FEATURE_FILE_PATHS[kind].format(slug=slug)
        if file_path.exists():
            parts.append(file_path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _extract_shared_file_paths(root: Path, slug_a: str, slug_b: str) -> list[str]:
    paths_a: set[str] = set()
    paths_b: set[str] = set()
    for kind in FEATURE_FILE_PATHS:
        file_path = root / FEATURE_FILE_PATHS[kind].format(slug=slug_a)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    paths_a.add(stripped.lower())

        file_path = root / FEATURE_FILE_PATHS[kind].format(slug=slug_b)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    paths_b.add(stripped.lower())

    shared = sorted(paths_a & paths_b)
    return [p for p in shared if len(p) > 3]


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

    node_map: dict[str, dict[str, object]] = {}
    for slug in valid_slugs:
        metadata = read_feature_metadata(resolved_root, slug)
        node_map[slug] = {
            "slug": slug,
            "effort": metadata.effort,
            "milestone": metadata.milestone,
        }

    explicit_edges: list[DependencyEdge] = []
    adj: dict[str, set[str]] = {slug: set() for slug in valid_slugs}

    for slug in valid_slugs:
        content = _read_all_feature_content(resolved_root, slug)
        referenced_slugs = _extract_slugs_from_text(content, slug, set(valid_slugs))
        for ref_slug in referenced_slugs:
            if ref_slug in node_map and ref_slug not in adj[slug]:
                adj[slug].add(ref_slug)
                reason = f"Explicit reference in {slug} artifacts"
                explicit_edges.append(
                    DependencyEdge(
                        from_slug=slug,
                        to_slug=ref_slug,
                        reason=reason,
                        inference="explicit",
                    )
                )

    # Note: Implicit dependencies from shared milestones or file paths are NOT created
    # because they produce O(n^2) edges which are not meaningful dependencies.
    # Only explicit content-based dependencies are tracked.

    for slug in valid_slugs:
        node_map[slug]["dep_count"] = len(adj[slug])

    topo_order = _topological_sort(valid_slugs, adj)
    cycles = _detect_cycles(valid_slugs, adj)

    if topo_order is not None and valid_slugs:
        critical = _compute_critical_path(node_map, adj, topo_order)
    else:
        critical = {"path": [], "total_effort": 0}

    nodes = [
        DependencyNode(
            slug=node_map[s]["slug"],
            effort=node_map[s]["effort"],
            milestone=node_map[s]["milestone"],
            dep_count=node_map[s]["dep_count"],
        )
        for s in valid_slugs
    ]

    edges = explicit_edges

    filter_desc = feature_slugs[0] if feature_slugs and len(feature_slugs) == 1 else None

    recommended: list[str] = []
    if cycles:
        cycle_slugs = ", ".join(c[0] for c in cycles if c)
        recommended.append(
            f"Resolve cycles before implementation: {cycle_slugs}"
        )
    if topo_order:
        recommended.append(
            "Recommended implementation order: " + " -> ".join(topo_order)
        )
    if critical["path"]:
        recommended.append(
            f"Critical path ({critical['total_effort']} effort): {' -> '.join(critical['path'])}"
        )
    if not recommended:
        recommended.append("No dependencies detected; features can be implemented independently.")
    for slug in valid_slugs:
        recommended.append(
            f"specspine feature handoff {slug} . --json"
        )

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


def render_dependency_json(result: dict[str, object]) -> str:
    return json.dumps(result, indent=2, sort_keys=False) + "\n"


def render_dependency_text(result: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append(f"Dependency graph for {result['root']}")
    if result["feature_filter"]:
        lines.append(f"Feature filter: {result['feature_filter']}")
    lines.append("")

    nodes: list[dict[str, object]] = result["nodes"]
    lines.append(f"Nodes ({len(nodes)}):")
    for node in nodes:
        dep_info = f" ({node['dep_count']} deps)" if node["dep_count"] else ""
        lines.append(
            f"  - {node['slug']}: effort={node['effort']}, milestone={node['milestone']}{dep_info}"
        )
    lines.append("")

    edges: list[dict[str, object]] = result["edges"]
    lines.append(f"Edges ({len(edges)}):")
    if edges:
        for edge in edges:
            lines.append(
                f"  - {edge['from']} -> {edge['to']} [{edge['inference']}]: {edge['reason']}"
            )
    else:
        lines.append("  (none)")
    lines.append("")

    topo = result["topological_order"]
    if topo:
        lines.append(f"Topological order: {' -> '.join(topo)}")
    else:
        lines.append("Topological order: N/A (cycles detected)")
    lines.append("")

    cycles = result["cycles"]
    if cycles:
        lines.append(f"Cycles ({len(cycles)}):")
        for cycle in cycles:
            lines.append(f"  - {' -> '.join(cycle)}")
    else:
        lines.append("Cycles: none")
    lines.append("")

    critical = result["critical_path"]
    path = critical.get("path", [])
    effort = critical.get("total_effort", 0)
    if path:
        lines.append(f"Critical path ({effort} effort): {' -> '.join(path)}")
    else:
        lines.append("Critical path: N/A")
    lines.append("")

    commands = result["recommended_commands"]
    if commands:
        lines.append("Recommended commands:")
        for cmd in commands:
            lines.append(f"  {cmd}")

    return "\n".join(lines) + "\n"
