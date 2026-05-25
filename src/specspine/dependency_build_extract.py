"""Re-export dependency extraction from sub-package."""

from __future__ import annotations

from .dependency_build_extract import (
    _extract_shared_file_paths,
    _extract_slugs_from_text,
    _list_feature_slugs,
    _read_all_feature_content,
)

__all__ = [
    "_extract_shared_file_paths",
    "_extract_slugs_from_text",
    "_list_feature_slugs",
    "_read_all_feature_content",
]
