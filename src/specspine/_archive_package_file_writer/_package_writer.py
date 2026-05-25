from __future__ import annotations

from pathlib import Path

from ..archive_models import FeatureArchiveReport
from ..archive_render import feature_archive_report_with_package, render_feature_archive_json, render_feature_archive_text
from .._archive_paths import _source_snapshot_path

__all__ = [
    "_write_archive_metadata",
    "_write_archive_source_files",
]


def _write_archive_metadata(
    package,
    report: FeatureArchiveReport,
) -> None:
    package_report = feature_archive_report_with_package(report, package)
    package.readme_path.write_text(
        render_feature_archive_text(package_report),
        encoding="utf-8",
    )
    package.report_path.write_text(
        render_feature_archive_json(package_report),
        encoding="utf-8",
    )


def _write_archive_source_files(
    report: FeatureArchiveReport,
    resolved_output_dir: Path,
) -> None:
    for kind, file in report.status_report.files.items():
        if not bool(file["exists"]):
            continue
        relative_path = str(file["path"])
        source_path = report.workspace_root / relative_path
        target = resolved_output_dir / _source_snapshot_path(kind)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
