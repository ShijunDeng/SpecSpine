from __future__ import annotations

from pathlib import Path

from ..dependency import _topological_sort
from ..features import validate_feature_slug

from .orchestration_detection import (
    _detect_contract_conflicts,
    _detect_file_conflicts,
    _detect_semantic_conflicts,
)
from .orchestration_planning_graph import (
    _build_dependency_graph,
    _compute_parallel_groups,
)
from .orchestration_models import OrchestrationPlan

__all__ = [
    "_resolve_slugs",
    "_detect_conflicts",
    "_compute_plan",
]


def _resolve_slugs(
    resolved_root: Path,
    all_slugs: list[str],
    feature_filter: str | None,
) -> str | None:
    if feature_filter is not None:
        try:
            feature_filter = validate_feature_slug(feature_filter)
        except ValueError:
            raise
    if feature_filter is not None:
        slugs = [feature_filter] if feature_filter in all_slugs else []
    else:
        slugs = list(all_slugs)
    return slugs


def _detect_conflicts(
    resolved_root: Path,
    slugs: list[str],
) -> list:
    file_conflicts = _detect_file_conflicts(resolved_root, slugs)
    contract_conflicts = _detect_contract_conflicts(resolved_root, slugs)
    semantic_conflicts = _detect_semantic_conflicts(slugs, resolved_root)
    return file_conflicts + contract_conflicts + semantic_conflicts


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
