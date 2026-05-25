from __future__ import annotations

from pathlib import Path

from .consistency_models import (
    ConsistencyReference,
)
from .consistency_utils import (
    _dedupe_references,
)

__all__ = [
    "_coverage_references",
    "_changed_references",
]


def _coverage_references(report) -> tuple[ConsistencyReference, ...]:
    references = []
    for link in report.test_coverage:
        if not link.target_path.startswith("tests/"):
            continue
        references.append(
            ConsistencyReference(
                path=link.target_path,
                line=link.line,
                kind="test",
                matched=link.acceptance_criterion_id,
                exists=link.target_exists,
            )
        )
    return _dedupe_references(references)


def _changed_references(
    *,
    root: Path,
    slug: str,
    changed_files: tuple[str, ...],
    source_files: tuple[str, ...],
    implementation_references: tuple[ConsistencyReference, ...],
    test_references: tuple[ConsistencyReference, ...],
    documentation_references: tuple[ConsistencyReference, ...],
) -> tuple[ConsistencyReference, ...]:
    known_paths = set(source_files)
    known_paths.update(reference.path for reference in implementation_references)
    known_paths.update(reference.path for reference in test_references)
    known_paths.update(reference.path for reference in documentation_references)
    references = []
    for changed_file in changed_files:
        if changed_file in known_paths:
            matched = "feature evidence path"
        elif slug in changed_file:
            matched = slug
        else:
            continue
        references.append(
            ConsistencyReference(
                path=changed_file,
                line=None,
                kind="changed",
                matched=matched,
                exists=(root / changed_file).exists(),
            )
        )
    return tuple(references)
