from __future__ import annotations

from pathlib import Path

from .features import FEATURE_FILE_PATHS

__all__ = [
    "_read_feature_content",
]


def _read_feature_content(
    slug: str,
    resolved_root: Path,
) -> str:
    spec_path = resolved_root / FEATURE_FILE_PATHS["spec"].format(slug=slug)
    execution_path = resolved_root / FEATURE_FILE_PATHS["execution"].format(slug=slug)

    contents: list[str] = []
    for path in (spec_path, execution_path):
        if path.exists():
            try:
                contents.append(path.read_text(encoding="utf-8"))
            except OSError:
                pass

    return "\n".join(contents)
