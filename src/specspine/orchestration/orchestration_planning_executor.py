from __future__ import annotations

from pathlib import Path

from ..dependency import _list_feature_slugs
from ._plan_resolver import _resolve_slugs, _detect_conflicts, _compute_plan
from ._plan_assembler import _assemble_orchestration_report
from .orchestration_models import OrchestrationReport

__all__ = [
    "build_orchestration_plan",
]


def build_orchestration_plan(
    root: Path,
    feature_filter: str | None = None,
) -> OrchestrationReport:
    resolved_root = root.expanduser().resolve()

    all_slugs = _list_feature_slugs(resolved_root)

    slugs = _resolve_slugs(resolved_root, all_slugs, feature_filter)

    all_conflicts = _detect_conflicts(resolved_root, slugs)

    plan, topo_order, adj = _compute_plan(resolved_root, slugs, all_conflicts)

    return _assemble_orchestration_report(
        resolved_root=resolved_root,
        feature_filter=feature_filter,
        all_conflicts=all_conflicts,
        plan=plan,
        topo_order=topo_order,
        slugs=slugs,
        adj=adj,
    )
