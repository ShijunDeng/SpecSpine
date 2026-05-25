from __future__ import annotations

from pathlib import Path

from ..hygiene_models import HygieneFinding
from ..hygiene_scanner_utils import _relative_path, _generated_file_source, _add_finding

__all__ = [
    "_check_blocked_path",
    "_check_generated_artifact",
]


def _check_blocked_path(
    root: Path,
    path: Path,
    findings: list[HygieneFinding],
    *,
    blocked_paths: set[str],
) -> bool:
    """Check if path is a forbidden path remnant. Returns True if blocked."""
    relative_path = _relative_path(root, path)
    if relative_path in blocked_paths:
        _add_finding(
            findings,
            finding_id="forbidden-path-remnant",
            severity="critical",
            category="forbidden_path",
            path=relative_path,
            message="Forbidden path remnant exists.",
            source="forbidden-path",
        )
        return True
    return False


def _check_generated_artifact(
    root: Path,
    path: Path,
    state,
    findings: list[HygieneFinding],
) -> bool:
    """Check if path is a generated/cache artifact. Returns True if generated."""
    relative_path = _relative_path(root, path)
    generated_source = _generated_file_source(path)
    if generated_source is not None:
        _add_finding(
            findings,
            finding_id="generated-file-artifact",
            severity="low",
            category="generated_artifact",
            path=relative_path,
            message="Generated or cache artifact is present.",
            source=generated_source,
        )
        state.skip_file("generated_artifact")
        return True
    return False
