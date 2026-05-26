from __future__ import annotations

from ._graph_collector import _collect_graph_data
from ._graph_analyzer import _analyze_graph_structure
from ._graph_assembler import _assemble_graph_result

__all__ = [
    "build_dependency_graph",
]


def build_dependency_graph(
    root,
    feature_slugs: list[str] | None = None,
) -> dict[str, object]:
    from pathlib import Path
    resolved_root = root.expanduser().resolve() if isinstance(root, Path) else Path(str(root)).expanduser().resolve()

    collected = _collect_graph_data(resolved_root, feature_slugs)

    analyzed = _analyze_graph_structure(
        collected["valid_slugs"],
        collected["adj"],
        collected["node_map"],
    )

    return _assemble_graph_result(
        resolved_root,
        feature_slugs,
        collected["valid_slugs"],
        collected["node_map"],
        collected["explicit_edges"],
        analyzed["topo_order"],
        analyzed["cycles"],
        analyzed["critical"],
    )
