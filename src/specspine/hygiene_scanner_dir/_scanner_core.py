from __future__ import annotations

from pathlib import Path

from ..hygiene_models import (
    HygieneFinding,
    _ScanState,
)
from ..hygiene_scanner_utils import (
    _relative_path,
)
from ._scanner_actions import (
    _handle_directory_entry,
    _handle_file_entry,
)

__all__ = [
    "_scan_directory",
]


def _scan_directory(
    root: Path,
    path: Path,
    state: _ScanState,
    findings: list[HygieneFinding],
    *,
    blocked_paths: set[str],
    blocked_patterns: tuple[str, ...],
) -> None:
    try:
        entries = sorted(path.iterdir(), key=lambda item: item.name)
    except OSError as error:
        state.skip_directory("iter_error:" + error.__class__.__name__)
        return

    for entry in entries:
        relative_path = _relative_path(root, entry)
        try:
            if entry.is_symlink():
                state.skip_file("symlink")
                continue
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
                continue
            if entry.is_file():
                _handle_file_entry(
                    entry,
                    root,
                    state,
                    findings,
                    blocked_paths=blocked_paths,
                    blocked_patterns=blocked_patterns,
                )
                continue
        except OSError as error:
            state.skip_file("stat_error:" + error.__class__.__name__)
            continue
        state.skip_file("special_file")
