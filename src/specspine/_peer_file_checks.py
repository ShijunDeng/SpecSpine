from __future__ import annotations

from pathlib import Path

from .features import FEATURE_FILE_PATHS
from .validation_models import ValidationCheck
from ._peer_file_existence import _check_peer_file_existence
from ._peer_file_content import _check_peer_file_content

__all__ = [
    "_check_peer_files",
]


def _check_peer_files(
    root: Path,
    slug: str,
) -> tuple[list[ValidationCheck], dict[str, str], bool]:
    checks, existing_files = _check_peer_file_existence(root, slug)
    statuses_by_kind: dict[str, str] = {}
    status_missing = False

    for kind, target in existing_files.items():
        relative_path = FEATURE_FILE_PATHS[kind].format(slug=slug)
        content_checks, status_value, file_status_missing = _check_peer_file_content(
            slug, kind, target, relative_path
        )
        checks.extend(content_checks)
        if status_value is not None:
            statuses_by_kind[kind] = status_value
        if file_status_missing:
            status_missing = True

    return checks, statuses_by_kind, status_missing
