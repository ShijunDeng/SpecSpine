from __future__ import annotations

from pathlib import Path

from .validation_models import ValidationCheck
from ._peer_slug_validation import _validate_peer_slug
from ._peer_file_checks import _check_peer_files
from ._peer_status_consistency import _check_status_consistency

__all__ = [
    "_feature_peer_checks",
]


def _feature_peer_checks(root: Path, slug: str) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []

    slug_checks, slug_valid = _validate_peer_slug(slug)
    checks.extend(slug_checks)
    if not slug_valid:
        return checks

    file_checks, statuses_by_kind, status_missing = _check_peer_files(root, slug)
    checks.extend(file_checks)

    consistency_checks = _check_status_consistency(slug, statuses_by_kind, status_missing)
    checks.extend(consistency_checks)

    return checks
