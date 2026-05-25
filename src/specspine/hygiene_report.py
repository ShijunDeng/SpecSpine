from __future__ import annotations

from pathlib import Path
from typing import Any

from .hygiene_models import (
    CATEGORIES,
    SEVERITIES,
    HygieneFinding,
    HygieneReport,
    _ScanState,
)
from .hygiene_scanner import (
    _blocked_content_patterns,
    _blocked_path_remnants,
    _dedupe,
    _normalise_changed_file,
    _scan_directory,
)

__all__ = [
    "_summary",
    "_recommended_commands",
    "build_hygiene_scan_report",
    "hygiene_report_has_strict_findings",
]


def _summary(
    findings: tuple[HygieneFinding, ...],
    *,
    changed_files: tuple[str, ...],
    state: _ScanState,
) -> dict[str, Any]:
    by_severity = {severity: 0 for severity in SEVERITIES}
    by_category: dict[str, int] = {category: 0 for category in CATEGORIES}
    for finding in findings:
        by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
        by_category[finding.category] = by_category.get(finding.category, 0) + 1
    return {
        "by_category": dict(sorted(by_category.items())),
        "by_severity": by_severity,
        "changed_files": len(changed_files),
        "directories_scanned": state.directories_scanned,
        "directories_skipped": state.directories_skipped,
        "files_scanned": state.files_scanned,
        "files_skipped": state.files_skipped,
        "findings_total": len(findings),
        "skipped_reasons": dict(sorted((state.skipped_reasons or {}).items())),
    }


def _recommended_commands(changed_files: tuple[str, ...]) -> tuple[str, ...]:
    commands = [
        "specspine hygiene scan . --json",
        "specspine hygiene scan . --strict --json",
    ]
    for path in changed_files:
        commands.append(f"specspine hygiene scan . --changed {path} --json")
    return _dedupe(commands)


def build_hygiene_scan_report(
    root: Path,
    *,
    changed_files: tuple[str, ...] = (),
) -> HygieneReport:
    resolved_root = root.expanduser().resolve()
    if not resolved_root.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved_root}")
    if not resolved_root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {resolved_root}")

    normalised_changed_files = _dedupe(
        [_normalise_changed_file(resolved_root, path) for path in changed_files]
    )
    state = _ScanState()
    findings: list[HygieneFinding] = []
    _scan_directory(
        resolved_root,
        resolved_root,
        state,
        findings,
        blocked_paths=set(_blocked_path_remnants()),
        blocked_patterns=_blocked_content_patterns(),
    )
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
    safety_notes = (
        "This scan reads local workspace files only.",
        "It does not delete files, run tests, invoke subprocesses, call network services, call GitHub, invoke upstream CLIs, read environment variables, or read tokens.",
        "Binary, symlinked, generated, and unreadable files are skipped rather than treated as clean.",
    )
    return HygieneReport(
        root=resolved_root,
        changed_files=normalised_changed_files,
        findings=sorted_findings,
        summary=_summary(
            sorted_findings,
            changed_files=normalised_changed_files,
            state=state,
        ),
        recommended_commands=_recommended_commands(normalised_changed_files),
        safety_notes=safety_notes,
    )


def hygiene_report_has_strict_findings(report: HygieneReport) -> bool:
    counts = report.summary["by_severity"]
    return bool(counts.get("critical", 0) or counts.get("high", 0))
