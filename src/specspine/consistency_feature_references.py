from __future__ import annotations

from pathlib import Path

from ._consistency_file_discovery import _discover_feature_files
from ._consistency_reference_gathering import _gather_all_references

__all__ = [
    "_gather_feature_references",
]


def _gather_feature_references(
    root: Path,
    slug: str,
    *,
    changed_files: tuple[str, ...],
) -> dict:
    discovery = _discover_feature_files(root, slug)
    references = _gather_all_references(
        root,
        slug,
        source_files=discovery["source_files"],
        explicit_paths=discovery["explicit_paths"],
        changed_files=changed_files,
    )
    return {
        "source_files": discovery["source_files"],
        "missing_files": discovery["missing_files"],
        "implementation_references": references["implementation_references"],
        "test_references": references["test_references"],
        "documentation_references": references["documentation_references"],
        "changed_references": references["changed_references"],
    }
