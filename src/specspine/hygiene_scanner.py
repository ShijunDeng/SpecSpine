from __future__ import annotations

from pathlib import Path

from .hygiene_models import (
    CONTENT_SCAN_EXCLUDED_PATHS,
    GENERATED_FILE_NAMES,
    GENERATED_FILE_SUFFIXES,
    GENERATED_DIRECTORY_NAMES,
    VCS_DIRECTORY_NAMES,
    HygieneFinding,
    _ScanState,
)

__all__ = [
    "_join",
    "_blocked_lower_name",
    "_blocked_path_remnants",
    "_blocked_content_patterns",
    "_relative_path",
    "_display_directory",
    "_normalise_changed_file",
    "_dedupe",
    "_generated_file_source",
    "_read_text",
    "_add_finding",
    "_scan_text_file",
    "_scan_file",
    "_scan_directory",
]


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
