from __future__ import annotations

from pathlib import Path

from .archive_models import FeatureArchivePackage, FeatureArchiveReport
from .archive_render import feature_archive_report_with_package, render_feature_archive_json, render_feature_archive_text
from ._archive_paths import _source_snapshot_path
from ._archive_targets import _archive_write_targets


def write_feature_archive_package(
    report: FeatureArchiveReport,
    output_dir: Path,
    *,
    force: bool = False,
) -> FeatureArchivePackage:
    resolved_output_dir = output_dir.expanduser().resolve()
    if resolved_output_dir.exists() and not resolved_output_dir.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {resolved_output_dir}")

    write_targets = _archive_write_targets(report, resolved_output_dir)
    parent_conflicts = tuple(
        path
        for path in write_targets
        if path.parent.exists() and not path.parent.is_dir()
    )
    if parent_conflicts:
        raise NotADirectoryError(
            f"Output archive parent is not a directory: {parent_conflicts[0]}"
        )

    existing_paths = tuple(path for path in write_targets if path.exists())
    if existing_paths and not force:
        from .archive_models import FeatureArchiveArtifactExistsError
        raise FeatureArchiveArtifactExistsError(
            output_dir=resolved_output_dir,
            existing_paths=existing_paths,
        )

    package = FeatureArchivePackage(
        output_dir=resolved_output_dir,
        readme_path=resolved_output_dir / "README.md",
        report_path=resolved_output_dir / "archive.json",
        source_paths=tuple(
            resolved_output_dir / _source_snapshot_path(kind)
            for kind, file in report.status_report.files.items()
            if bool(file["exists"])
        ),
        written_paths=write_targets,
    )
    package_report = feature_archive_report_with_package(report, package)

    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    package.readme_path.write_text(
        render_feature_archive_text(package_report),
        encoding="utf-8",
    )
    package.report_path.write_text(
        render_feature_archive_json(package_report),
        encoding="utf-8",
    )

    for kind, file in report.status_report.files.items():
        if not bool(file["exists"]):
            continue
        relative_path = str(file["path"])
        source_path = report.workspace_root / relative_path
        target = resolved_output_dir / _source_snapshot_path(kind)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")

    return package


__all__ = [
    "write_feature_archive_package",
]
