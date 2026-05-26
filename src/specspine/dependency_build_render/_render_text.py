from __future__ import annotations

from ._render_header import _render_header
from ._render_graph import _render_nodes, _render_edges
from ._render_analysis import (
    _render_topo_order,
    _render_cycles,
    _render_critical_path,
    _render_commands,
)


def render_dependency_text(result: dict[str, object]) -> str:
    lines: list[str] = []
    lines.extend(_render_header(result))
    lines.extend(_render_nodes(result))
    lines.extend(_render_edges(result))
    lines.extend(_render_topo_order(result))
    lines.extend(_render_cycles(result))
    lines.extend(_render_critical_path(result))
    lines.extend(_render_commands(result))
    return "\n".join(lines) + "\n"


__all__ = [
    "render_dependency_text",
]
