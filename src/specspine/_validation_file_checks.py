from __future__ import annotations

from pathlib import Path

from .validation_models import ValidationCheck
from ._validation_helpers import _check, _relative_paths
from .workspace import check_workspace


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


__all__ = [
    "_file_checks",
]
