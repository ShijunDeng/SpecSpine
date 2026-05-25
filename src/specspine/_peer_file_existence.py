from __future__ import annotations

from pathlib import Path

from .features import FEATURE_FILE_PATHS
from .validation_feature_helpers import _check
from .validation_models import ValidationCheck

__all__ = [
    "_check_peer_file_existence",
]


def _check_peer_file_existence(
    root: Path,
    slug: str,
) -> tuple[list[ValidationCheck], dict[str, Path]]:
    checks: list[ValidationCheck] = []
    existing_files: dict[str, Path] = {}

    for kind, pattern in FEATURE_FILE_PATHS.items():
        relative_path = pattern.format(slug=slug)
        target = root / relative_path
        if target.exists():
            checks.append(
                _check(
                    f"feature.required_file:{slug}:{kind}",
                    "pass",
                    f"Feature {slug} {kind} file exists: {relative_path}",
                )
            )
            existing_files[kind] = target
        else:
            checks.append(
                _check(
                    f"feature.required_file:{slug}:{kind}",
                    "fail",
                    f"Feature {slug} {kind} file is missing: {relative_path}",
                )
            )

    return checks, existing_files
