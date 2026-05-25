from __future__ import annotations

from pathlib import Path

from .consistency_models import (
    ConsistencyReference,
    DOCUMENTATION_GLOBS,
    IMPLEMENTATION_GLOBS,
    TEST_GLOBS,
)
from .consistency_utils import (
    _area_prefixes,
    _candidate_files,
    _dedupe_references,
    _read_text,
    _relative_path,
)

__all__ = [
    "_references_for_area",
]


def _references_for_area(
    root: Path,
    *,
    slug: str,
    explicit_paths: set[str],
    globs: tuple[str, ...],
    area: str,
) -> tuple[ConsistencyReference, ...]:
    references = []
    seen = set()
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

    for path in _candidate_files(root, globs):
        relative_path = _relative_path(root, path)
        content = _read_text(path)
        for line_number, line in enumerate(content.splitlines(), start=1):
            if slug not in line:
                continue
            key = (relative_path, line_number, area, slug)
            if key in seen:
                continue
            references.append(
                ConsistencyReference(
                    path=relative_path,
                    line=line_number,
                    kind=area,
                    matched=slug,
                    exists=True,
                )
            )
            seen.add(key)
    return tuple(_dedupe_references(references))
