from __future__ import annotations

__all__ = [
    "_render_topo_order",
    "_render_cycles",
    "_render_critical_path",
    "_render_commands",
]


def _render_topo_order(result: dict[str, object]) -> list[str]:
    lines: list[str] = []
    topo = result["topological_order"]
    if topo:
        lines.append(f"Topological order: {' -> '.join(topo)}")
    else:
        lines.append("Topological order: N/A (cycles detected)")
    lines.append("")
    return lines


def _render_cycles(result: dict[str, object]) -> list[str]:
    lines: list[str] = []
    cycles = result["cycles"]
    if cycles:
        lines.append(f"Cycles ({len(cycles)}):")
        for cycle in cycles:
            lines.append(f"  - {' -> '.join(cycle)}")
    else:
        lines.append("Cycles: none")
    lines.append("")
    return lines


def _render_critical_path(result: dict[str, object]) -> list[str]:
    lines: list[str] = []
    critical = result["critical_path"]
    path = critical.get("path", [])
    effort = critical.get("total_effort", 0)
    if path:
        lines.append(f"Critical path ({effort} effort): {' -> '.join(path)}")
    else:
        lines.append("Critical path: N/A")
    lines.append("")
    return lines


def _render_commands(result: dict[str, object]) -> list[str]:
    lines: list[str] = []
    commands = result["recommended_commands"]
    if commands:
        lines.append("Recommended commands:")
        for cmd in commands:
            lines.append(f"  {cmd}")
    return lines
