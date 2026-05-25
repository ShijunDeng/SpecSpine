from __future__ import annotations

from pathlib import Path

from ..hygiene_models import (
    CONTENT_SCAN_EXCLUDED_PATHS,
    HygieneFinding,
    _ScanState,
)
from ..hygiene_scanner_utils import _relative_path, _read_text
from ..hygiene_scanner_text import _scan_text_file

__all__ = [
    "_scan_file_content",
]


def _scan_file_content(
    root: Path,
    path: Path,
    state: _ScanState,
    findings: list[HygieneFinding],
    *,
    blocked_patterns: tuple[str, ...],
) -> None:
    relative_path = _relative_path(root, path)

    if relative_path in CONTENT_SCAN_EXCLUDED_PATHS:
        state.skip_file("content_scan_excluded")
        return

    text, skipped_reason = _read_text(path)
    if skipped_reason is not None:
        state.skip_file(skipped_reason)
        return
    if text is None:
        state.skip_file("read_skipped")
        return

    state.files_scanned += 1
    _scan_text_file(
        findings,
        relative_path=relative_path,
        text=text,
        patterns=blocked_patterns,
    )
