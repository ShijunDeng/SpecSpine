from __future__ import annotations

import json


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


__all__ = [
    "render_dependency_json",
    "render_dependency_text",
]
