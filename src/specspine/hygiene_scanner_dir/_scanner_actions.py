from __future__ import annotations

from typing import TYPE_CHECKING

from ..hygiene_models import (
    HygieneFinding,
    _ScanState,
)
from ..hygiene_scanner_file import _scan_file
from ..hygiene_scanner_utils import (
    _add_finding,
    _display_directory,
    _relative_path,
)
from ._filters import _is_generated_directory, _is_vcs_directory

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "_handle_directory_entry",
    "_handle_file_entry",
]


def _handle_directory_entry(
    entry: "Path",
    root: "Path",
    state: _ScanState,
    findings: list[HygieneFinding],
    relative_path: str,
    *,
    blocked_paths: set[str],
    blocked_patterns: tuple[str, ...],
) -> None:
    from ._scanner_core import _scan_directory

    if _is_generated_directory(entry.name):
        _add_finding(
            findings,
            finding_id="generated-cache-directory",
            severity="low",
            category="generated_artifact",
            path=_display_directory(relative_path),
            message="Generated or cache directory is present.",
            source=entry.name,
        )
        state.skip_directory("generated_artifact")
        return
    if _is_vcs_directory(entry.name):
        state.skip_directory("vcs_directory")
        return
    state.directories_scanned += 1
    _scan_directory(
        root,
        entry,
        state,
        findings,
        blocked_paths=blocked_paths,
        blocked_patterns=blocked_patterns,
    )


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
