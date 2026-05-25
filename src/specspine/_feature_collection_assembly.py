from __future__ import annotations

from pathlib import Path

from ._feature_collection_assembly_entry import _build_release_entries
from .release_models import ReleaseEntry

__all__ = [
    "_collect_release_features",
]


def _collect_release_features(
    root: Path,
    since: str | None = None,
    until: str | None = None,
) -> list[ReleaseEntry]:
    return _build_release_entries(root, since, until)
