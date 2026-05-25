from __future__ import annotations

from ..evolution_impact_models import ImpactEntry

__all__ = [
    "resolve_removed_ac_impact",
    "resolve_modified_ac_impact",
]


def resolve_removed_ac_impact(
    change,
    change_has_refs: dict[str, list[str]],
    downstream: dict[str, list[dict]],
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
    coverage_refs = downstream.get("coverage", [])
    for cov_ref in coverage_refs:
        if cov_ref.get("feature_id") in [r.get("feature_id") for r in refs]:
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="coverage",
                    affected_id=cov_ref.get("coverage_id", "unknown"),
                    severity="breaking",
                )
            )

    impacts.append(
        ImpactEntry(
            change_id=change.change_id,
            affected_type="ac",
            affected_id=change.after or change.before or "unknown",
            severity="warning",
        )
    )
    return impacts


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
