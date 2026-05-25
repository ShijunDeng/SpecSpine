from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..features import (
    FeatureReadyReport,
    FeatureStatusReport,
    FeatureTasksReport,
    FeatureTestsReport,
    FeatureTraceReport,
)
from ._archive_report_serialization import _build_archive_dict
from ._archive_report_summary import _build_archive_summary
from .archive_package import FeatureArchivePackage

__all__ = [
    "FeatureArchiveReport",
]


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
        return _build_archive_summary(self)

    def as_dict(self) -> dict[str, object]:
        return _build_archive_dict(self)
