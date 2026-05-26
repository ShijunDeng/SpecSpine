from __future__ import annotations

from pathlib import Path

from ..hygiene_models import (
    HygieneFinding,
    _ScanState,
)
from ._scanner_actions import (
    _handle_directory_entry,
    _handle_file_entry,
)

__all__ = [
    "_dispatch_entry",
]


def _dispatch_entry(
    entry: Path,
    root: Path,
    state: _ScanState,
    findings: list[HygieneFinding],
    relative_path: str,
    *,
    blocked_paths: set[str],
    blocked_patterns: tuple[str, ...],
) -> bool:
    """Dispatch a single directory entry based on its type.

    Returns True if the entry was handled, False if it should be skipped.
    """
    if entry.is_symlink():
        state.skip_file("symlink")
        return True
    if entry.is_dir():
        _handle_directory_entry(
            entry,
            root,
            state,
            findings,
            relative_path,
            blocked_paths=blocked_paths,
            blocked_patterns=blocked_patterns,
        )
        return True
    if entry.is_file():
        _handle_file_entry(
            entry,
            root,
            state,
            findings,
            blocked_paths=blocked_paths,
            blocked_patterns=blocked_patterns,
        )
        return True
    return False
