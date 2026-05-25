from __future__ import annotations

from pathlib import Path

from .dependency import build_dependency_graph
from .evolution_classification import ClassifiedChange
from .features import validate_feature_slug
from .evolution_impact_downstream import _find_downstream_references
from .evolution_impact_models import ImpactEntry, ImpactResult


def resolve_impact(
    changes: list[ClassifiedChange],
    slug: str,
    root: Path,
) -> ImpactResult:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    downstream = _find_downstream_references(slug, resolved_root)
    impacts: list[ImpactEntry] = []
    impact_counter = 0

    change_has_refs: dict[str, list[str]] = {}
    for ref_type, refs in downstream.items():
        for ref in refs:
            feature_id = ref.get("feature_id", "")
            for change in changes:
                if change.change_type in ("removed", "modified"):
                    if feature_id not in change_has_refs:
                        change_has_refs[change.change_id] = []
                    if feature_id not in change_has_refs[change.change_id]:
                        change_has_refs[change.change_id].append(feature_id)

    for change in changes:
        if change.change_type == "removed" and change.category == "ac":
            refs = change_has_refs.get(change.change_id, [])
            for ref_feature in refs:
                impact_counter += 1
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
                    impact_counter += 1
                    impacts.append(
                        ImpactEntry(
                            change_id=change.change_id,
                            affected_type="coverage",
                            affected_id=cov_ref.get("coverage_id", "unknown"),
                            severity="breaking",
                        )
                    )

            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="ac",
                    affected_id=change.after or change.before or "unknown",
                    severity="warning",
                )
            )

        elif change.change_type == "modified" and change.category == "ac":
            refs = change_has_refs.get(change.change_id, [])
            for ref_feature in refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="feature",
                        affected_id=ref_feature,
                        severity="warning",
                    )
                )
            if not refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="ac",
                        affected_id=change.after or change.before or "unknown",
                        severity="info",
                    )
                )

        elif change.change_type == "removed" and change.category == "task":
            refs = change_has_refs.get(change.change_id, [])
            for ref_feature in refs:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type="feature",
                        affected_id=ref_feature,
                        severity="breaking",
                    )
                )
            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="task",
                    affected_id=change.before or "unknown",
                    severity="warning",
                )
            )

        elif change.change_type == "added":
            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type=change.category,
                    affected_id=change.after or "unknown",
                    severity="info",
                )
            )

        elif change.change_type == "modified" and change.category == "metadata":
            impact_counter += 1
            impacts.append(
                ImpactEntry(
                    change_id=change.change_id,
                    affected_type="metadata",
                    affected_id=slug,
                    severity="info",
                )
            )

        elif change.change_type == "modified" and change.category in ("spec", "execution", "quality"):
            refs = change_has_refs.get(change.change_id, [])
            if refs:
                for ref_feature in refs:
                    impact_counter += 1
                    impacts.append(
                        ImpactEntry(
                            change_id=change.change_id,
                            affected_type="feature",
                            affected_id=ref_feature,
                            severity="warning",
                        )
                    )
            else:
                impact_counter += 1
                impacts.append(
                    ImpactEntry(
                        change_id=change.change_id,
                        affected_type=change.category,
                        affected_id=slug,
                        severity="info",
                    )
                )

    return ImpactResult(slug=slug, impacts=impacts)


__all__ = [
    "resolve_impact",
]
