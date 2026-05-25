from __future__ import annotations

from pathlib import Path

from .features import FEATURE_FILE_PATHS

__all__ = [
    "_read_bundle_content",
]


def _read_bundle_content(
    resolved_root: Path,
    slug: str,
) -> tuple[str, str, str]:
    bundle_paths = {
        kind: resolved_root / FEATURE_FILE_PATHS[kind].format(slug=slug)
        for kind in FEATURE_FILE_PATHS
    }

    spec_path = bundle_paths["spec"]
    execution_path = bundle_paths["execution"]
    quality_path = bundle_paths["quality"]

    spec_content = ""
    if spec_path.exists():
        try:
            spec_content = spec_path.read_text(encoding="utf-8")
        except OSError:
            pass

    execution_content = ""
    if execution_path.exists():
        try:
            execution_content = execution_path.read_text(encoding="utf-8")
        except OSError:
            pass

    quality_content = ""
    if quality_path.exists():
        try:
            quality_content = quality_path.read_text(encoding="utf-8")
        except OSError:
            pass

    return spec_content, execution_content, quality_content
