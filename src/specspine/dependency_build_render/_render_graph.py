from __future__ import annotations

__all__ = [
    "_render_nodes",
    "_render_edges",
]


def _render_nodes(result: dict[str, object]) -> list[str]:
    lines: list[str] = []
    nodes: list[dict[str, object]] = result["nodes"]
    lines.append(f"Nodes ({len(nodes)}):")
    for node in nodes:
        dep_info = f" ({node['dep_count']} deps)" if node["dep_count"] else ""
        lines.append(
            f"  - {node['slug']}: effort={node['effort']}, milestone={node['milestone']}{dep_info}"
        )
    lines.append("")
    return lines


def _render_edges(result: dict[str, object]) -> list[str]:
    lines: list[str] = []
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
    return lines
