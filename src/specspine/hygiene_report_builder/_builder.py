from __future__ import annotations

from pathlib import Path

from ..hygiene_models import (
    HygieneFinding,
    HygieneReport,
    _ScanState,
)
from ..hygiene_report_summary import (
    _recommended_commands,
    _summary,
)
from ..hygiene_scanner import (
    _blocked_content_patterns,
    _blocked_path_remnants,
    _normalise_changed_file,
    _scan_directory,
)
from ..hygiene_scanner import _dedupe
from ._safety import HYGIENE_SAFETY_NOTES

__all__ = [
    "build_hygiene_scan_report",
]


def build_hygiene_scan_report(
    root: Path,
    *,
    changed_files: tuple[str, ...] = (),
) -> HygieneReport:
    resolved_root = root.expanduser().resolve()
    if not resolved_root.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved_root}")
    if not resolved_root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {resolved_root}")

    normalised_changed_files = _dedupe(
        [_normalise_changed_file(resolved_root, path) for path in changed_files]
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
    sorted_findings = tuple(
        sorted(
            findings,
            key=lambda finding: (
                finding.path,
                finding.line or 0,
                finding.category,
                finding.source,
            ),
        )
    )
    return HygieneReport(
        root=resolved_root,
        changed_files=normalised_changed_files,
        findings=sorted_findings,
        summary=_summary(
            sorted_findings,
            changed_files=normalised_changed_files,
            state=state,
        ),
        recommended_commands=_recommended_commands(normalised_changed_files),
        safety_notes=HYGIENE_SAFETY_NOTES,
    )
