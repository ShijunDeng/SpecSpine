from __future__ import annotations

from .consistency_models import (
    ConsistencyReference,
)
from .consistency_utils import (
    _area_prefixes,
)

__all__ = [
    "_references_for_area_explicit",
]


def _references_for_area_explicit(
    root,
    *,
    explicit_paths: set[str],
    area: str,
) -> tuple[ConsistencyReference, ...]:
    references = []
    for explicit_path in sorted(explicit_paths):
        if not explicit_path.startswith(_area_prefixes(area)):
            continue
        references.append(
            ConsistencyReference(
                path=explicit_path,
                line=None,
                kind=area,
                matched="explicit feature artifact path",
                exists=(root / explicit_path).exists(),
            )
        )
    return tuple(references)
