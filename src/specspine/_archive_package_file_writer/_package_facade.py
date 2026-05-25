from __future__ import annotations

from ._package_builder import _build_archive_package
from ._package_writer import _write_archive_metadata, _write_archive_source_files

__all__ = [
    "_build_archive_package",
    "_write_archive_metadata",
    "_write_archive_source_files",
    "write_archive_package_files",
]


def write_archive_package_files(
    report,
    resolved_output_dir,
    write_targets: tuple,
):
    package = _build_archive_package(report, resolved_output_dir, write_targets)
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    _write_archive_metadata(package, report)
    _write_archive_source_files(report, resolved_output_dir)
    return package
