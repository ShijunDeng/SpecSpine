from __future__ import annotations

from pathlib import Path

from ..dependency import _topological_sort
from .orchestration_models import OrchestrationPlan
from .orchestration_planning_graph import (
    _build_dependency_graph,
    _compute_parallel_groups,
)

__all__ = [
    "_compute_plan",
]


def _compute_plan(
    resolved_root: Path,
    slugs: list[str],
    all_conflicts: list,
) -> tuple[OrchestrationPlan, list[str] | None, dict]:
    adj = _build_dependency_graph(resolved_root, slugs)
    topo_order = _topological_sort(slugs, adj)
    if topo_order is None:
        topo_order = []
    else:
        topo_order = list(reversed(topo_order))

    parallel_groups = _compute_parallel_groups(topo_order, adj)

    has_blocking = any(c.severity in ("critical", "high") for c in all_conflicts)
    safe_for_parallel = len(parallel_groups) == 1 and not has_blocking

    blocked_features: list[str] = []
    for c in all_conflicts:
        if c.severity == "critical":
            for f in c.features_involved:
                if f not in blocked_features:
                    blocked_features.append(f)
    blocked_features.sort()

    return OrchestrationPlan(
        execution_order=tuple(topo_order),
        parallel_groups=tuple(parallel_groups),
        blocked_features=tuple(blocked_features),
        safe_for_parallel=safe_for_parallel,
    ), topo_order, adj
