from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


def _join(*parts: str) -> str:
    return "".join(parts)


def _blocked_lower_name() -> str:
    return _join("m", "cp")


def _blocked_path_remnants() -> tuple[str, ...]:
    lower_name = _blocked_lower_name()
    source_prefix = "src/specspine/"
    test_prefix = "tests/test_"
    return (
        source_prefix + _join("github", "_api") + ".py",
        source_prefix + _join("github", "_auth") + ".py",
        source_prefix + lower_name + ".py",
        source_prefix + "sync.py",
        source_prefix + "guard.py",
        test_prefix + "sync.py",
        test_prefix + "guard.py",
        test_prefix + lower_name + ".py",
    )


def _blocked_content_patterns() -> tuple[str, ...]:
    lower_name = _blocked_lower_name()
    return (
        lower_name,
        lower_name.upper(),
        lower_name + "-server",
        _join("github", "-remote-", "sync"),
        _join("github", "_api"),
        _join("github", "_auth"),
        _join("SPECSPINE_", "GITHUB", "_", "TOKEN"),
        _join("token", "-stdin"),
        _join("--", "github", "-token"),
        _join("sync", "_feature_to_", "github"),
        _join("FeatureStatus", "SyncError"),
        _join("g", "hp_"),
    )


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


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _display_directory(path: str) -> str:
    return path if path.endswith("/") else path + "/"


def _normalise_changed_file(root: Path, value: str) -> str:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    return _relative_path(root, candidate.resolve())


def _dedupe(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        deduped.append(value)
        seen.add(value)
    return tuple(deduped)


def _generated_file_source(path: Path) -> str | None:
    if path.name in GENERATED_FILE_NAMES:
        return path.name
    for suffix in GENERATED_FILE_SUFFIXES:
        if path.name.endswith(suffix):
            return "*" + suffix
    return None


def _read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        return None, "read_error:" + error.__class__.__name__
    if b"\0" in raw:
        return None, "binary"
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError:
        return None, "decode_error"


def _add_finding(
    findings: list[HygieneFinding],
    *,
    finding_id: str,
    severity: str,
    category: str,
    path: str,
    message: str,
    source: str,
    line: int | None = None,
) -> None:
    findings.append(
        HygieneFinding(
            id=finding_id,
            severity=severity,
            category=category,
            path=path,
            line=line,
            message=message,
            source=source,
        )
    )


def _scan_text_file(
    findings: list[HygieneFinding],
    *,
    relative_path: str,
    text: str,
    patterns: tuple[str, ...],
) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern in patterns:
            if pattern not in line:
                continue
            _add_finding(
                findings,
                finding_id="forbidden-content-pattern",
                severity="high",
                category="forbidden_content",
                path=relative_path,
                line=line_number,
                message="Forbidden content pattern detected.",
                source=pattern,
            )


def _scan_file(
    root: Path,
    path: Path,
    state: _ScanState,
    findings: list[HygieneFinding],
    *,
    blocked_paths: set[str],
    blocked_patterns: tuple[str, ...],
) -> None:
    relative_path = _relative_path(root, path)
    if relative_path in blocked_paths:
        _add_finding(
            findings,
            finding_id="forbidden-path-remnant",
            severity="critical",
            category="forbidden_path",
            path=relative_path,
            message="Forbidden path remnant exists.",
            source="forbidden-path",
        )

    generated_source = _generated_file_source(path)
    if generated_source is not None:
        _add_finding(
            findings,
            finding_id="generated-file-artifact",
            severity="low",
            category="generated_artifact",
            path=relative_path,
            message="Generated or cache artifact is present.",
            source=generated_source,
        )
        state.skip_file("generated_artifact")
        return

    if relative_path in CONTENT_SCAN_EXCLUDED_PATHS:
        state.skip_file("content_scan_excluded")
        return

    text, skipped_reason = _read_text(path)
    if skipped_reason is not None:
        state.skip_file(skipped_reason)
        return
    if text is None:
        state.skip_file("read_skipped")
        return

    state.files_scanned += 1
    _scan_text_file(
        findings,
        relative_path=relative_path,
        text=text,
        patterns=blocked_patterns,
    )


def _scan_directory(
    root: Path,
    path: Path,
    state: _ScanState,
    findings: list[HygieneFinding],
    *,
    blocked_paths: set[str],
    blocked_patterns: tuple[str, ...],
) -> None:
    try:
        entries = sorted(path.iterdir(), key=lambda item: item.name)
    except OSError as error:
        state.skip_directory("iter_error:" + error.__class__.__name__)
        return

    for entry in entries:
        relative_path = _relative_path(root, entry)
        try:
            if entry.is_symlink():
                state.skip_file("symlink")
                continue
            if entry.is_dir():
                if entry.name in GENERATED_DIRECTORY_NAMES:
                    _add_finding(
                        findings,
                        finding_id="generated-cache-directory",
                        severity="low",
                        category="generated_artifact",
                        path=_display_directory(relative_path),
                        message="Generated or cache directory is present.",
                        source=entry.name,
                    )
                    state.skip_directory("generated_artifact")
                    continue
                if entry.name in VCS_DIRECTORY_NAMES:
                    state.skip_directory("vcs_directory")
                    continue
                state.directories_scanned += 1
                _scan_directory(
                    root,
                    entry,
                    state,
                    findings,
                    blocked_paths=blocked_paths,
                    blocked_patterns=blocked_patterns,
                )
                continue
            if entry.is_file():
                _scan_file(
                    root,
                    entry,
                    state,
                    findings,
                    blocked_paths=blocked_paths,
                    blocked_patterns=blocked_patterns,
                )
                continue
        except OSError as error:
            state.skip_file("stat_error:" + error.__class__.__name__)
            continue
        state.skip_file("special_file")


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


def render_hygiene_scan_json(report: HygieneReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_hygiene_scan_text(report: HygieneReport) -> str:
    summary = report.summary
    severity = summary["by_severity"]
    lines = [
        f"Repository hygiene scan: {report.root}",
        (
            "Summary: "
            f"changed_files={summary['changed_files']} "
            f"findings_total={summary['findings_total']} "
            f"critical={severity['critical']} "
            f"high={severity['high']} "
            f"medium={severity['medium']} "
            f"low={severity['low']} "
            f"files_scanned={summary['files_scanned']} "
            f"files_skipped={summary['files_skipped']}"
        ),
        "Findings:",
    ]
    if report.findings:
        for finding in report.findings:
            location = finding.path
            if finding.line is not None:
                location = f"{location}:{finding.line}"
            lines.append(
                "- "
                f"{finding.severity} {finding.category} "
                f"{location} [{finding.source}] - {finding.message}"
            )
    else:
        lines.append("- None.")

    lines.append("Recommended commands:")
    for command in report.recommended_commands:
        lines.append(f"- {command}")

    lines.append("Safety notes:")
    for note in report.safety_notes:
        lines.append(f"- {note}")

    return "\n".join(lines) + "\n"
