from __future__ import annotations

from pathlib import Path
from typing import Any

from .impact_models import ImpactItem
from ._dependency_graph import _build_downstream_map
from ._impact_scorer import _score_feature_impact, _analyze_shared_paths

__all__ = [
    "_find_affected_features",
]


def _find_affected_features(
    slug: str,
    root: Path,
    proposed_changes: dict[str, Any] | None = None,
) -> list[ImpactItem]:
    resolved_root = root.expanduser().resolve()
    downstream = _build_downstream_map(slug, resolved_root)
    if not downstream:
        return []

    from ..dependency import _list_feature_slugs
    all_slugs = _list_feature_slugs(resolved_root)

    affected: list[ImpactItem] = []
    seen: set[str] = set()
    affected.extend(_score_feature_impact(slug, downstream, resolved_root, seen))

    if proposed_changes and "shared_paths" in proposed_changes:
        affected.extend(_analyze_shared_paths(slug, proposed_changes, all_slugs, resolved_root, seen))

    return affected
