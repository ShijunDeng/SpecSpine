from __future__ import annotations

from pathlib import Path

from ..dependency import (
    _list_feature_slugs,
    _topological_sort,
)

from ..features import validate_feature_slug

from .orchestration_detection import (
    _detect_contract_conflicts,
    _detect_file_conflicts,
    _detect_semantic_conflicts,
)
from .orchestration_models import (
    OrchestrationPlan,
    OrchestrationReport,
)
from .orchestration_planning_graph import (
    _build_dependency_graph,
    _compute_parallel_groups,
)
from .orchestration_planning_recs import _generate_integration_recommendations

__all__ = [
    "_build_dependency_graph",
    "_compute_parallel_groups",
    "_generate_integration_recommendations",
    "build_orchestration_plan",
]


def build_orchestration_plan(
    root: Path,
    feature_filter: str | None = None,
) -> OrchestrationReport:
    resolved_root = root.expanduser().resolve()

    all_slugs = _list_feature_slugs(resolved_root)

    if feature_filter is not None:
        try:
            feature_filter = validate_feature_slug(feature_filter)
        except ValueError:
            raise

    if feature_filter is not None:
        slugs = [feature_filter] if feature_filter in all_slugs else []
    else:
        slugs = list(all_slugs)

    file_conflicts = _detect_file_conflicts(resolved_root, slugs)
    contract_conflicts = _detect_contract_conflicts(resolved_root, slugs)
    semantic_conflicts = _detect_semantic_conflicts(slugs, resolved_root)
    all_conflicts = file_conflicts + contract_conflicts + semantic_conflicts

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

    plan = OrchestrationPlan(
        execution_order=tuple(topo_order),
        parallel_groups=tuple(parallel_groups),
        blocked_features=tuple(blocked_features),
        safe_for_parallel=safe_for_parallel,
    )

    integration_recs = _generate_integration_recommendations(all_conflicts, topo_order, adj)

    blocking_items: list[str] = []
    for c in all_conflicts:
        if c.severity in ("critical", "high"):
            blocking_items.append(
                f"[{c.severity.upper()}] {c.conflict_type} conflict: {c.description}"
            )

    if topo_order is None or (slugs and not topo_order):
        blocking_items.append("Dependency cycle detected; topological order cannot be computed.")

    status = "ok"
    if blocking_items:
        status = "blocked" if any(c.severity == "critical" for c in all_conflicts) else "warnings"

    safety_notes = (
        "This report reads local workspace files only.",
        "Recommended commands are advisory only and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
    )

    return OrchestrationReport(
        root=str(resolved_root),
        feature_filter=feature_filter,
        conflicts=tuple(all_conflicts),
        plan=plan,
        integration_recommendations=tuple(integration_recs),
        status=status,
        blocking_items=tuple(blocking_items),
        safety_notes=safety_notes,
    )
