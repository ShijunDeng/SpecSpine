from __future__ import annotations

from pathlib import Path

from ._peer_file_reader import _read_peer_file
from ._peer_file_validators import _validate_peer_feature_id, _validate_peer_status
from .validation_models import ValidationCheck

__all__ = [
    "_check_peer_file_content",
]


def _check_peer_file_content(
    slug: str,
    kind: str,
    target: Path,
    relative_path: str,
) -> tuple[list[ValidationCheck], str | None, bool]:
    checks: list[ValidationCheck] = []
    status_value: str | None = None
    status_missing = False

    content, read_checks = _read_peer_file(slug, kind, target, relative_path)
    checks.extend(read_checks)
    if content is None:
        return checks, status_value, True

    checks.append(_validate_peer_feature_id(slug, kind, content))

    status_check, status_value, status_missing = _validate_peer_status(
        slug, kind, content
    )
    checks.append(status_check)

    return checks, status_value, status_missing
