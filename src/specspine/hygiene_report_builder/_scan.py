from __future__ import annotations

from pathlib import Path

from ..hygiene_models import HygieneFinding, _ScanState
from ..hygiene_scanner import (
    _blocked_content_patterns,
    _blocked_path_remnants,
    _dedupe,
    _normalise_changed_file,
    _scan_directory,
)

__all__ = [
    "collect_hygiene_findings",
]


def collect_hygiene_findings(
    resolved_root: Path,
    changed_files: tuple[str, ...],
) -> tuple[Path, tuple[str, ...], list[HygieneFinding], _ScanState]:
    normalised_changed_files = tuple(
        _dedupe(
            [_normalise_changed_file(resolved_root, path) for path in changed_files]
        )
    )
    state = _ScanState()
    findings: list[HygieneFinding] = []
    _scan_directory(
        resolved_root,
        resolved_root,
        state,
        findings,
        blocked_paths=set(_blocked_path_remnants()),
        blocked_patterns=_blocked_content_patterns(),
    )
    return resolved_root, normalised_changed_files, findings, state
