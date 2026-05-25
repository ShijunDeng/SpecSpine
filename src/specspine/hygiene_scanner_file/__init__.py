from __future__ import annotations

from pathlib import Path

from ..hygiene_models import (
    HygieneFinding,
    _ScanState,
)
from ._file_checks import _check_blocked_path, _check_generated_artifact
from ._content_scan import _scan_file_content

__all__ = [
    "_scan_file",
]


def _scan_file(
    root: Path,
    path: Path,
    state: _ScanState,
    findings: list[HygieneFinding],
    *,
    blocked_paths: set[str],
    blocked_patterns: tuple[str, ...],
) -> None:
    _check_blocked_path(root, path, findings, blocked_paths=blocked_paths)

    if _check_generated_artifact(root, path, state, findings):
        return

    _scan_file_content(
        root,
        path,
        state,
        findings,
        blocked_patterns=blocked_patterns,
    )
