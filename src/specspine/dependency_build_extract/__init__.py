"""Dependency extraction from feature files."""

from __future__ import annotations

from pathlib import Path

from ._extract_slug_patterns import _extract_slugs_from_text
from ._extract_feature_io import _list_feature_slugs, _read_all_feature_content
from ._extract_shared_paths import _extract_shared_file_paths

__all__ = [
    "_extract_shared_file_paths",
    "_extract_slugs_from_text",
    "_list_feature_slugs",
    "_read_all_feature_content",
]
