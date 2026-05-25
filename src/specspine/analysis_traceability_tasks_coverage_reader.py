from __future__ import annotations

from .features import (
    FEATURE_FILE_PATHS,
    feature_bundle_paths,
    parse_test_coverage,
)

__all__ = [
    "_read_test_coverage",
]


def _read_test_coverage(
    root,
    slug: str,
):
    from pathlib import Path
    quality_path = feature_bundle_paths(root, slug)["quality"]
    if not quality_path.exists():
        return ()
    quality_file = FEATURE_FILE_PATHS["quality"].format(slug=slug)
    quality_content = quality_path.read_text(encoding="utf-8")
    return parse_test_coverage(
        quality_content,
        source_file=quality_file,
        root=root,
    )
