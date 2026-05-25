from __future__ import annotations

from pathlib import Path

from .archive_models import (
    ARCHIVE_ID_RE,
    TEST_COVERAGE_HEADING_RE,
    FeatureArchiveReport,
    FeatureStatusReport,
    InvalidArchiveId,
)
from .features import feature_bundle_paths


def validate_archive_id(archive_id: str) -> str:
    if ARCHIVE_ID_RE.fullmatch(archive_id):
        return archive_id
    raise InvalidArchiveId(
        f"Invalid archive id '{archive_id}'. Use letters, numbers, dots, "
        "underscores, and hyphens; start with a letter or number."
    )


def _default_archive_id(slug: str) -> str:
    return f"{slug}-archive"


def _coverage_section_exists(root: Path, slug: str) -> bool:
    quality_path = feature_bundle_paths(root, slug)["quality"]
    if not quality_path.exists():
        return False
    return bool(
        TEST_COVERAGE_HEADING_RE.search(quality_path.read_text(encoding="utf-8"))
    )


def _source_and_missing_files(
    status_report: FeatureStatusReport,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    source_files = tuple(
        str(file["path"])
        for file in status_report.files.values()
        if bool(file["exists"])
    )
    missing_files = tuple(str(path) for path in status_report.missing_files)
    return source_files, missing_files


def _archive_safety_notes(coverage_required: bool) -> tuple[str, ...]:
    notes = [
        (
            "This command only reads local SpecSpine feature artifacts unless "
            "--output-dir is provided."
        ),
        (
            "When --output-dir is provided, this command writes only the "
            "explicit output directory and does not mark the feature archived."
        ),
        (
            "The archive package preserves local evidence for review; use the "
            "recommended lifecycle command separately after reviewing readiness."
        ),
        (
            "SpecSpine did not run tests, invoke subprocesses, call network "
            "services, invoke upstream CLIs, call GitHub APIs, or read tokens."
        ),
    ]
    if coverage_required:
        notes.append(
            "A local Test Coverage section was present, so archive readiness "
            "uses the same coverage gate as feature ready --require-coverage."
        )
    return tuple(notes)


def _archive_recommended_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature ready {slug} . --json",
        f"specspine feature ready {slug} . --json --require-coverage",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine feature status {slug} . --set archived --enforce-transition --json",
        "specspine validate . --fusion --features --json",
    )


__all__ = [
    "validate_archive_id",
    "_default_archive_id",
    "_coverage_section_exists",
    "_source_and_missing_files",
    "_archive_safety_notes",
    "_archive_recommended_commands",
]
