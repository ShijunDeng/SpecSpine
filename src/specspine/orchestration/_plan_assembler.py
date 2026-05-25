from __future__ import annotations

from .orchestration_models import OrchestrationPlan, OrchestrationReport
from .orchestration_planning_recs import _generate_integration_recommendations

__all__ = [
    "_assemble_orchestration_report",
]


def _assemble_orchestration_report(
    resolved_root: Path,
    feature_filter: str | None,
    all_conflicts: list,
    plan: OrchestrationPlan,
    topo_order: list[str] | None,
    slugs: list[str],
    adj: dict,
) -> OrchestrationReport:
    integration_recs = _generate_integration_recommendations(
        all_conflicts, topo_order if topo_order else [], adj
    )

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
