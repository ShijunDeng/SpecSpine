from __future__ import annotations

from typing import Any

from ..dependency import topological_sort


def _topo_sort_steps(steps: list[dict[str, Any]]) -> list[str]:
    if not steps:
        return []
    nodes = [{"slug": s["step_id"]} for s in steps]
    edges: list[dict[str, str]] = []
    step_ids = {s["step_id"] for s in steps}
    for s in steps:
        for dep in s["dependency_step_ids"]:
            if dep in step_ids:
                edges.append({"from": dep, "to": s["step_id"]})
    order = topological_sort(nodes, edges)
    if order is not None:
        return order
    return [s["step_id"] for s in steps]


__all__ = [
    "_topo_sort_steps",
]
