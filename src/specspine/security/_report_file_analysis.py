from __future__ import annotations

from pathlib import Path
from typing import Any

from .helpers import (
    _classify_changed_file,
    _dedupe,
    _is_within_root,
    _read_small_text,
)
from .detectors import _detect_cues

__all__ = [
    "_analyze_changed_files",
]


def _analyze_changed_files(
    resolved_root: Path,
    normalised_changed_files: list[str],
    resolved_by_path: dict[str, Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int], int]:
    files: list[dict[str, Any]] = []
    cues: list[dict[str, Any]] = []
    categories: dict[str, int] = {}
    files_existing = 0

    for path in normalised_changed_files:
        resolved_path = resolved_by_path[path]
        category = _classify_changed_file(path)
        exists = resolved_path.exists()
        if exists:
            files_existing += 1
        categories[category] = categories.get(category, 0) + 1

        file_info: dict[str, Any] = {
            "category": category,
            "exists": exists,
            "path": path,
        }
        text: str | None = None
        if exists:
            if _is_within_root(resolved_root, resolved_path):
                text, skipped_reason = _read_small_text(resolved_path)
                file_info["text_read"] = text is not None
                if skipped_reason is not None:
                    file_info["read_skipped"] = skipped_reason
            else:
                file_info["text_read"] = False
                file_info["read_skipped"] = "outside_root"
        else:
            file_info["text_read"] = False
        files.append(file_info)

        if text is not None:
            found = _detect_cues(path, category, text)
            cues.extend(found)

    return files, cues, categories, files_existing
