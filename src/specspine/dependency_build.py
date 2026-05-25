from __future__ import annotations

import json
from pathlib import Path

from .dependency_algorithms import (
    _compute_critical_path,
    _detect_cycles,
    _topological_sort,
)
from .dependency_models import (
    DEFAULT_EFFORT,
    EFFORT_VALUES,
    EXPLICIT_DEP_PATTERNS,
    _resolve_effort,
    DependencyEdge,
    DependencyGraphResult,
    DependencyNode,
)
from .features import (
    FEATURE_DIRECTORIES,
    FEATURE_FILE_PATHS,
    read_feature_metadata,
)

__all__ = [
    "_extract_slugs_from_text",
    "_list_feature_slugs",
    "_read_all_feature_content",
    "_extract_shared_file_paths",
    "build_dependency_graph",
    "render_dependency_json",
    "render_dependency_text",
]


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
