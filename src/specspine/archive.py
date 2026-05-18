from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .features import (
    FeatureBundleNotFoundError,
    FeatureReadyReport,
    FeatureStatusReport,
    FeatureTasksReport,
    FeatureTestsReport,
    FeatureTraceReport,
    build_feature_ready_report,
    build_feature_tasks_report,
    build_feature_tests_report,
    build_feature_trace_report,
    feature_bundle_paths,
    get_feature_status,
    read_feature_metadata,
    validate_feature_slug,
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


def build_feature_archive_report(
    root: Path,
    slug: str,
    *,
    archive_id: str | None = None,
) -> FeatureArchiveReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    resolved_archive_id = validate_archive_id(archive_id or _default_archive_id(slug))

    status_report = get_feature_status(resolved_root, slug)
    has_native_files = any(file["exists"] for file in status_report.files.values())
    if not has_native_files:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(feature_bundle_paths(resolved_root, slug).values()),
        )

    coverage_required = _coverage_section_exists(resolved_root, slug)
    ready_report = build_feature_ready_report(
        resolved_root,
        slug,
        require_coverage=coverage_required,
    )
    trace_report = build_feature_trace_report(resolved_root, slug)
    tasks_report = build_feature_tasks_report(resolved_root, slug)
    tests_report = build_feature_tests_report(resolved_root, slug)
    metadata = read_feature_metadata(resolved_root, slug).as_dict()
    source_files, missing_files = _source_and_missing_files(status_report)

    return FeatureArchiveReport(
        archive_id=resolved_archive_id,
        feature_id=slug,
        workspace_root=resolved_root,
        status=status_report.status or "unknown",
        ready=ready_report.ready,
        coverage_required=coverage_required,
        status_report=status_report,
        ready_report=ready_report,
        trace_report=trace_report,
        tasks_report=tasks_report,
        tests_report=tests_report,
        metadata=metadata,
        source_files=source_files,
        missing_files=missing_files,
        safety_notes=_archive_safety_notes(coverage_required),
        recommended_commands=_archive_recommended_commands(slug),
    )


def render_feature_archive_json(report: FeatureArchiveReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def feature_archive_report_with_package(
    report: FeatureArchiveReport,
    package: FeatureArchivePackage,
) -> FeatureArchiveReport:
    return FeatureArchiveReport(
        archive_id=report.archive_id,
        feature_id=report.feature_id,
        workspace_root=report.workspace_root,
        status=report.status,
        ready=report.ready,
        coverage_required=report.coverage_required,
        status_report=report.status_report,
        ready_report=report.ready_report,
        trace_report=report.trace_report,
        tasks_report=report.tasks_report,
        tests_report=report.tests_report,
        metadata=report.metadata,
        source_files=report.source_files,
        missing_files=report.missing_files,
        safety_notes=report.safety_notes,
        recommended_commands=report.recommended_commands,
        package=package,
    )


def render_feature_archive_text(report: FeatureArchiveReport) -> str:
    summary = report.summary
    lines = [
        f"# Feature Archive Package Plan: {report.feature_id}",
        "",
        "## Summary",
        "",
        f"- Archive ID: {report.archive_id}",
        f"- Status: {report.status}",
        f"- Ready: {'yes' if report.ready else 'no'}",
        f"- Coverage required: {'yes' if report.coverage_required else 'no'}",
        (
            "- Evidence: "
            f"sources={summary['source_files']['total']} "
            f"missing={summary['missing_files']['total']} "
            f"trace_items={summary['trace']['total']} "
            f"tasks={summary['tasks']['total']} "
            f"test_coverage={summary['test_coverage']['total']} "
            f"blocking={summary['blocking_checks']['total']} "
            f"gaps={summary['gaps']['total']}"
        ),
        "",
        "## Metadata",
        "",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(report.metadata.items()))
    lines.extend(["", "## Source Files", ""])
    if report.source_files:
        lines.extend(f"- [ok] {path}" for path in report.source_files)
    if report.missing_files:
        lines.extend(f"- [missing] {path}" for path in report.missing_files)
    if not report.source_files and not report.missing_files:
        lines.append("- None.")

    lines.extend(["", "## Blocking Checks", ""])
    if report.ready_report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.ready_report.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Gaps", ""])
    if report.trace_report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.trace_report.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Safety Notes", ""])
    lines.extend(f"- {note}" for note in report.safety_notes)

    lines.extend(["", "## Recommended Commands", ""])
    lines.extend(f"- `{command}`" for command in report.recommended_commands)

    if report.package is not None:
        lines.extend(
            [
                "",
                "## Written Package",
                "",
                f"- Output directory: {report.package.output_dir}",
                f"- Report: {report.package.report_path}",
                f"- Summary: {report.package.readme_path}",
            ]
        )
        lines.extend(f"- Source snapshot: {path}" for path in report.package.source_paths)

    return "\n".join(lines).rstrip() + "\n"


def _source_snapshot_path(kind: str) -> Path:
    return Path("sources") / f"{kind}.md"


def _archive_write_targets(
    report: FeatureArchiveReport,
    output_dir: Path,
) -> tuple[Path, ...]:
    targets = [
        output_dir / "README.md",
        output_dir / "archive.json",
    ]
    for kind, file in report.status_report.files.items():
        if bool(file["exists"]):
            targets.append(output_dir / _source_snapshot_path(kind))
    return tuple(targets)


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
        path.parent
        for path in write_targets
        if path.parent.exists() and not path.parent.is_dir()
    )
    if parent_conflicts:
        raise NotADirectoryError(
            f"Output archive parent is not a directory: {parent_conflicts[0]}"
        )

    existing_paths = tuple(path for path in write_targets if path.exists())
    if existing_paths and not force:
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
