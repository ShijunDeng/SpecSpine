from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._hygiene_findings import HygieneFinding

__all__ = [
    "HygieneReport",
    "_ScanState",
]


@dataclass(frozen=True)
class HygieneReport:
    root: Path
    changed_files: tuple[str, ...]
    findings: tuple[HygieneFinding, ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "changed_files": list(self.changed_files),
            "findings": [finding.as_dict() for finding in self.findings],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
        }


@dataclass
class _ScanState:
    files_scanned: int = 0
    files_skipped: int = 0
    directories_scanned: int = 0
    directories_skipped: int = 0
    skipped_reasons: dict[str, int] | None = None

    def skip_file(self, reason: str) -> None:
        self.files_skipped += 1
        self._record_skip(reason)

    def skip_directory(self, reason: str) -> None:
        self.directories_skipped += 1
        self._record_skip(reason)

    def _record_skip(self, reason: str) -> None:
        if self.skipped_reasons is None:
            self.skipped_reasons = {}
        self.skipped_reasons[reason] = self.skipped_reasons.get(reason, 0) + 1
