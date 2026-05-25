from __future__ import annotations

from ..evolution_impact_models import ImpactEntry


def resolve_modified_ac_impact(
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
                severity="warning",
            )
        )
    if not refs:
        impacts.append(
            ImpactEntry(
                change_id=change.change_id,
                affected_type="ac",
                affected_id=change.after or change.before or "unknown",
                severity="info",
            )
        )
    return impacts


__all__ = [
    "resolve_modified_ac_impact",
]
