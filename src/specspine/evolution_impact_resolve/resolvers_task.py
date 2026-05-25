from __future__ import annotations

from ..evolution_impact_models import ImpactEntry

__all__ = [
    "resolve_removed_task_impact",
    "resolve_added_impact",
]


def resolve_removed_task_impact(
    change,
    change_has_refs: dict[str, list[str]],
) -> list[ImpactEntry]:
    impacts: list[ImpactEntry] = []
    refs = change_has_refs.get(change.change_id, [])
    for ref_feature in refs:
        impacts.append(
            ImpactEntry(
                change_id=change.change_id,
                affected_type="feature",
                affected_id=ref_feature,
                severity="breaking",
            )
        )
    impacts.append(
        ImpactEntry(
            change_id=change.change_id,
            affected_type="task",
            affected_id=change.before or "unknown",
            severity="warning",
        )
    )
    return impacts


def resolve_added_impact(change) -> list[ImpactEntry]:
    return [
        ImpactEntry(
            change_id=change.change_id,
            affected_type=change.category,
            affected_id=change.after or "unknown",
            severity="info",
        )
    ]
