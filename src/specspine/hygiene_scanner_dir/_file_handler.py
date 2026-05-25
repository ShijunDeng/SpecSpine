from __future__ import annotations

from typing import TYPE_CHECKING

from ..hygiene_models import (
    HygieneFinding,
    _ScanState,
)
from ..hygiene_scanner_file import _scan_file

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "_handle_file_entry",
]


def _handle_file_entry(
    entry: "Path",
    root: "Path",
    state: _ScanState,
    findings: list[HygieneFinding],
    *,
    blocked_paths: set[str],
    blocked_patterns: tuple[str, ...],
) -> None:
    _scan_file(
        root,
        entry,
        state,
        findings,
        blocked_paths=blocked_paths,
        blocked_patterns=blocked_patterns,
    )
