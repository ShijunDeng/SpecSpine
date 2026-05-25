from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .features import (
    FeatureReadyReport,
    FeatureStatusReport,
    FeatureTasksReport,
    FeatureTestsReport,
    FeatureTraceReport,
)

ARCHIVE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
TEST_COVERAGE_HEADING_RE = re.compile(
    r"^#{2,6}\s+Test Coverage\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)


class InvalidArchiveId(ValueError):
    """Raised when an archive id cannot be used safely in a local package."""


@dataclass(frozen=True)
class FeatureArchiveArtifactExistsError(FileExistsError):
    output_dir: Path
    existing_paths: tuple[Path, ...]

    def __str__(self) -> str:
        return (
            f"Feature archive package files already exist in {self.output_dir}. "
            "Use --force to overwrite files written by this command."
        )


@dataclass(frozen=True)
class FeatureArchivePackage:
    output_dir: Path
    readme_path: Path
    report_path: Path
    source_paths: tuple[Path, ...]
    written_paths: tuple[Path, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "output_dir": str(self.output_dir),
            "readme": str(self.readme_path),
            "report": str(self.report_path),
            "sources": [str(path) for path in self.source_paths],
            "written_paths": [str(path) for path in self.written_paths],
        }


@dataclass(frozen=True)
class FeatureArchiveReport:
    archive_id: str
    feature_id: str
    workspace_root: Path
    status: str
    ready: bool
    coverage_required: bool
    status_report: FeatureStatusReport
    ready_report: FeatureReadyReport
    trace_report: FeatureTraceReport
    tasks_report: FeatureTasksReport
    tests_report: FeatureTestsReport
    metadata: dict[str, str]
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    safety_notes: tuple[str, ...]
    recommended_commands: tuple[str, ...]
    package: FeatureArchivePackage | None = None

    @property
    def summary(self) -> dict[str, object]:
        return {
            "blocking_checks": {
                "total": len(self.ready_report.blocking_checks),
            },
            "gaps": {
                "total": len(self.trace_report.gaps),
            },
            "missing_files": {
                "total": len(self.missing_files),
            },
            "ready": dict(self.ready_report.summary),
            "source_files": {
                "total": len(self.source_files),
            },
            "tasks": dict(self.tasks_report.summary),
            "test_coverage": dict(self.tests_report.summary["test_coverage"]),
            "test_plan": dict(self.tests_report.summary["test_plan"]),
            "trace": dict(self.trace_report.summary),
        }

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "archive_id": self.archive_id,
            "coverage_required": self.coverage_required,
            "feature_id": self.feature_id,
            "metadata": dict(self.metadata),
            "missing_files": list(self.missing_files),
            "ready": self.ready,
            "ready_report": self.ready_report.as_dict(),
            "recommended_commands": list(self.recommended_commands),
            "safety_notes": list(self.safety_notes),
            "source_files": list(self.source_files),
            "status": self.status,
            "status_report": self.status_report.as_dict(),
            "summary": self.summary,
            "tasks_report": self.tasks_report.as_dict(),
            "tests_report": self.tests_report.as_dict(),
            "trace_report": self.trace_report.as_dict(),
        }
        if self.package is not None:
            payload["package"] = self.package.as_dict()
        return payload


__all__ = [
    "ARCHIVE_ID_RE",
    "TEST_COVERAGE_HEADING_RE",
    "InvalidArchiveId",
    "FeatureArchiveArtifactExistsError",
    "FeatureArchivePackage",
    "FeatureArchiveReport",
]
