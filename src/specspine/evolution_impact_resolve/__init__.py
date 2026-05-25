from __future__ import annotations

from pathlib import Path

from ..dependency import build_dependency_graph  # noqa: F401
from ..evolution_classification import ClassifiedChange
from ..features import validate_feature_slug
from ..evolution_impact_downstream import _find_downstream_references
from ..evolution_impact_models import ImpactEntry, ImpactResult
from .resolvers import (
    resolve_removed_ac_impact,
    resolve_modified_ac_impact,
    resolve_removed_task_impact,
    resolve_added_impact,
    resolve_modified_metadata_impact,
    resolve_modified_spec_execution_quality_impact,
)

__all__ = [
    "resolve_impact",
]


def resolve_impact(
    changes: list[ClassifiedChange],
    slug: str,
    root: Path,
) -> ImpactResult:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    downstream = _find_downstream_references(slug, resolved_root)
    impacts: list[ImpactEntry] = []

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
            impacts.extend(resolve_removed_ac_impact(change, change_has_refs, downstream))

        elif change.change_type == "modified" and change.category == "ac":
            impacts.extend(resolve_modified_ac_impact(change, change_has_refs))

        elif change.change_type == "removed" and change.category == "task":
            impacts.extend(resolve_removed_task_impact(change, change_has_refs))

        elif change.change_type == "added":
            impacts.extend(resolve_added_impact(change))

        elif change.change_type == "modified" and change.category == "metadata":
            impacts.extend(resolve_modified_metadata_impact(change, slug))

        elif change.change_type == "modified" and change.category in ("spec", "execution", "quality"):
            impacts.extend(resolve_modified_spec_execution_quality_impact(change, change_has_refs, slug))

    return ImpactResult(slug=slug, impacts=impacts)
