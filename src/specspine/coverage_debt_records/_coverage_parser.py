from __future__ import annotations

from ..features import parse_test_coverage

__all__ = [
    "_parse_quality_coverage",
]


def _parse_quality_coverage(quality_path, *, source_file: str, root) -> tuple:
    if not quality_path.exists():
        return ()
    quality_content = quality_path.read_text(encoding="utf-8")
    return parse_test_coverage(
        quality_content,
        source_file=source_file,
        root=root,
    )
