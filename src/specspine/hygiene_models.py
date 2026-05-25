from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "GENERATED_DIRECTORY_NAMES",
    "GENERATED_FILE_NAMES",
    "GENERATED_FILE_SUFFIXES",
    "CONTENT_SCAN_EXCLUDED_PATHS",
    "VCS_DIRECTORY_NAMES",
    "SEVERITIES",
    "CATEGORIES",
    "HygieneFinding",
    "HygieneReport",
    "_ScanState",
]

GENERATED_DIRECTORY_NAMES = ("__pycache__", ".pytest_cache")
GENERATED_FILE_NAMES = (".DS_Store",)
GENERATED_FILE_SUFFIXES = (".pyc", ".pyo")
CONTENT_SCAN_EXCLUDED_PATHS = (
    "src/specspine/hygiene.py",
    "tests/test_hygiene.py",
)
VCS_DIRECTORY_NAMES = (".git", ".hg", ".svn")
SEVERITIES = ("critical", "high", "medium", "low")
CATEGORIES = ("forbidden_content", "forbidden_path", "generated_artifact")


@dataclass(frozen=True)
class HygieneFinding:
    id: str
    severity: str
    category: str
    path: str
    message: str
    source: str
    line: int | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "category": self.category,
            "id": self.id,
            "message": self.message,
            "path": self.path,
            "severity": self.severity,
            "source": self.source,
        }
        if self.line is not None:
            payload["line"] = self.line
        return payload


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
