from __future__ import annotations

from pathlib import Path

from ..hygiene_models import HygieneFinding, HygieneReport, _ScanState
from ..hygiene_report_summary import (
    _recommended_commands,
    _summary,
)
from ._safety import HYGIENE_SAFETY_NOTES

__all__ = [
    "assemble_hygiene_report",
]


def assemble_hygiene_report(
    resolved_root: Path,
    changed_files: tuple[str, ...],
    findings: list[HygieneFinding],
    state: _ScanState,
) -> HygieneReport:
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
        changed_files=changed_files,
        findings=sorted_findings,
        summary=_summary(
            sorted_findings,
            changed_files=changed_files,
            state=state,
        ),
        recommended_commands=_recommended_commands(changed_files),
        safety_notes=HYGIENE_SAFETY_NOTES,
    )
