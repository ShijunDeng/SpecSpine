from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .validation_models import ValidationCheck, VALIDATION_STATUSES, WORKSPACE_PLACEHOLDER_PHRASES
from .workspace import BASE_WORKSPACE_FILES, check_workspace


def _check(
    check_id: str,
    status: str,
    message: str,
    *,
    severity: str | None = None,
) -> ValidationCheck:
    if status not in VALIDATION_STATUSES:
        raise ValueError(f"Unsupported validation status: {status}")

    if severity is None:
        severity = {
            "fail": "error",
            "warn": "warning",
            "pass": "info",
            "skip": "info",
        }[status]

    return ValidationCheck(
        id=check_id,
        status=status,
        message=message,
        severity=severity,
    )


def _relative_paths(paths: Iterable[Path], root: Path) -> set[str]:
    return {str(path.relative_to(root)) for path in paths}


def _file_checks(
    root: Path,
    *,
    required_files: dict[str, str],
    prefix: str,
    label: str,
) -> list[ValidationCheck]:
    present_paths, missing_paths = check_workspace(root, required_files=required_files)
    present = _relative_paths(present_paths, root)
    missing = _relative_paths(missing_paths, root)

    checks: list[ValidationCheck] = []
    for relative_path in sorted(required_files):
        if relative_path in missing:
            checks.append(
                _check(
                    f"{prefix}.required_file:{relative_path}",
                    "fail",
                    f"{label} required file is missing: {relative_path}",
                )
            )
            continue

        if relative_path in present:
            checks.append(
                _check(
                    f"{prefix}.required_file:{relative_path}",
                    "pass",
                    f"{label} required file exists: {relative_path}",
                )
            )

    return checks


def _workspace_placeholder_checks(root: Path) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for relative_path, phrases in sorted(WORKSPACE_PLACEHOLDER_PHRASES.items()):
        target = root / relative_path
        if not target.exists():
            continue

        try:
            content = target.read_text(encoding="utf-8")
        except OSError:
            continue

        if any(phrase in content for phrase in phrases):
            checks.append(
                _check(
                    f"workspace.placeholder:{relative_path}",
                    "warn",
                    f"Workspace file still contains scaffold placeholder content: {relative_path}",
                )
            )

    return checks


__all__ = [
    "_check",
    "_file_checks",
    "_relative_paths",
    "_workspace_placeholder_checks",
]
