from __future__ import annotations

from pathlib import Path

from .consistency_models import (
    ConsistencyReference,
)
from .consistency_utils import (
    _candidate_files,
    _dedupe_references,
    _read_text,
    _relative_path,
)

__all__ = [
    "_references_for_area_content",
]


def _references_for_area_content(
    root: Path,
    *,
    slug: str,
    globs: tuple[str, ...],
    area: str,
) -> tuple[ConsistencyReference, ...]:
    references = []
    seen = set()
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
