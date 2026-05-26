from __future__ import annotations

from pathlib import Path

from .consistency_models import (
    ConsistencyReference,
    DOCUMENTATION_GLOBS,
    IMPLEMENTATION_GLOBS,
    TEST_GLOBS,
)
from .consistency_utils import _dedupe_references
from ._consistency_ref_area_explicit import _references_for_area_explicit
from ._consistency_ref_area_content import _references_for_area_content

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
    explicit_refs = _references_for_area_explicit(root, explicit_paths=explicit_paths, area=area)
    content_refs = _references_for_area_content(root, slug=slug, globs=globs, area=area)
    return tuple(_dedupe_references(list(explicit_refs) + list(content_refs)))
