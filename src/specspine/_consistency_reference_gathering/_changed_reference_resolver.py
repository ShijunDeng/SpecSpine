from __future__ import annotations

from pathlib import Path

from ..consistency_references import (
    _changed_references,
)

__all__ = [
    "_resolve_changed_references",
]


def _resolve_changed_references(
    root: Path,
    slug: str,
    *,
    source_files: list[str],
    changed_files: tuple[str, ...],
    implementation_references: list[str],
    test_references: list[str],
    documentation_references: list[str],
) -> list[str]:
    return _changed_references(
        root=root,
        slug=slug,
        changed_files=changed_files,
        source_files=source_files,
        implementation_references=implementation_references,
        test_references=test_references,
        documentation_references=documentation_references,
    )
