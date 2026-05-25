from __future__ import annotations

from .archive_models import (
    ARCHIVE_ID_RE,
    InvalidArchiveId,
)

__all__ = [
    "validate_archive_id",
    "_default_archive_id",
]


def validate_archive_id(archive_id: str) -> str:
    if ARCHIVE_ID_RE.fullmatch(archive_id):
        return archive_id
    raise InvalidArchiveId(
        f"Invalid archive id '{archive_id}'. Use letters, numbers, dots, "
        "underscores, and hyphens; start with a letter or number."
    )


def _default_archive_id(slug: str) -> str:
    return f"{slug}-archive"
