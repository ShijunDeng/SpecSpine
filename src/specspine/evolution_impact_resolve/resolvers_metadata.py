from __future__ import annotations

from ..evolution_impact_models import ImpactEntry

__all__ = [
    "resolve_modified_metadata_impact",
    "resolve_modified_spec_execution_quality_impact",
]


def resolve_modified_metadata_impact(change, slug: str) -> list[ImpactEntry]:
    return [
        ImpactEntry(
            change_id=change.change_id,
            affected_type="metadata",
            affected_id=slug,
            severity="info",
        )
    ]


def resolve_modified_spec_execution_quality_impact(
    change,
    change_has_refs: dict[str, list[str]],
    slug: str,
) -> list[ImpactEntry]:
    impacts: list[ImpactEntry] = []
    refs = change_has_refs.get(change.change_id, [])
    if refs:
        for ref_feature in refs:
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="feature",
                    affected_id=ref_feature,
                    severity="warning",
                )
            )
    else:
        impacts.append(
            ImpactEntry(
                change_id=change.change_id,
                affected_type=change.category,
                affected_id=slug,
                severity="info",
            )
        )
    return impacts
