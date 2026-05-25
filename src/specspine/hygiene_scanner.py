from __future__ import annotations

from pathlib import Path

from .hygiene_models import (
    CONTENT_SCAN_EXCLUDED_PATHS,
    GENERATED_DIRECTORY_NAMES,
    VCS_DIRECTORY_NAMES,
    HygieneFinding,
    _ScanState,
)
from .hygiene_scanner_utils import (
    _relative_path,
    _display_directory,
    _normalise_changed_file,
    _dedupe,
    _generated_file_source,
    _read_text,
    _add_finding,
)
from .hygiene_scanner_blocked import (
    _join,
    _blocked_lower_name,
    _blocked_path_remnants,
    _blocked_content_patterns,
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
