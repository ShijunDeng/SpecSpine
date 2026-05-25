from __future__ import annotations

from pathlib import Path

from ._reference_collector import _collect_references
from ._changed_reference_resolver import _resolve_changed_references

__all__ = [
    "_gather_all_references",
]


def _gather_all_references(
    root: Path,
    slug: str,
    *,
    source_files: list[str],
    explicit_paths: list[str],
    changed_files: tuple[str, ...],
) -> dict[str, list[str]]:
    collected = _collect_references(
        root,
        slug,
        explicit_paths=explicit_paths,
    )
    changed_reference_list = _resolve_changed_references(
        root=root,
        slug=slug,
        source_files=source_files,
        changed_files=changed_files,
        implementation_references=collected["implementation_references"],
        test_references=collected["test_references"],
        documentation_references=collected["documentation_references"],
    )
    return {
        "implementation_references": collected["implementation_references"],
        "test_references": collected["test_references"],
        "documentation_references": collected["documentation_references"],
        "changed_references": changed_reference_list,
    }
