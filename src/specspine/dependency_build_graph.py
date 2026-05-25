from __future__ import annotations

from pathlib import Path

from .dependency_algorithms import (
    _compute_critical_path,
    _detect_cycles,
    _topological_sort,
)
from .dependency_build_extract import (
    _extract_slugs_from_text,
    _list_feature_slugs,
    _read_all_feature_content,
)
from .dependency_models import (
    DependencyEdge,
    DependencyGraphResult,
    DependencyNode,
)
from .features import read_feature_metadata


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


__all__ = [
    "build_dependency_graph",
]
