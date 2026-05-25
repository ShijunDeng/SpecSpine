from __future__ import annotations

from pathlib import Path

from ..hygiene_models import (
    HygieneFinding,
    _ScanState,
)
from ..hygiene_scanner_utils import (
    _add_finding,
    _display_directory,
    _relative_path,
)
from ..hygiene_scanner_file import _scan_file
from ._filters import _is_generated_directory, _is_vcs_directory

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
                    continue
                if _is_vcs_directory(entry.name):
                    state.skip_directory("vcs_directory")
                    continue
                state.directories_scanned += 1
                _scan_directory(
                    root,
                    entry,
                    state,
                    findings,
                    blocked_paths=blocked_paths,
                    blocked_patterns=blocked_patterns,
                )
                continue
            if entry.is_file():
                _scan_file(
                    root,
                    entry,
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
