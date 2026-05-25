from __future__ import annotations

from pathlib import Path

from ._assemble import assemble_hygiene_report
from ._scan import collect_hygiene_findings
from ._validate import validate_scan_root

__all__ = [
    "build_hygiene_scan_report",
]


def build_hygiene_scan_report(
    root: Path,
    *,
    changed_files: tuple[str, ...] = (),
) -> HygieneReport:
    resolved_root = validate_scan_root(root)
    resolved_root, normalised_changed_files, findings, state = (
        collect_hygiene_findings(resolved_root, changed_files)
    )
    return assemble_hygiene_report(
        resolved_root,
        normalised_changed_files,
        findings,
        state,
    )
