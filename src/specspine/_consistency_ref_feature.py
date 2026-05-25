from __future__ import annotations

from pathlib import Path

from .consistency_models import (
    ConsistencyReference,
    DOCUMENTATION_GLOBS,
    IMPLEMENTATION_GLOBS,
    LOCAL_PATH_RE,
    TEST_GLOBS,
)
from .consistency_utils import (
    _area_prefixes,
    _candidate_files,
    _dedupe_references,
    _read_text,
    _relative_path,
)
from .features import (
    get_feature_status,
)

__all__ = [
    "_feature_source_files",
    "_feature_missing_files",
    "_explicit_paths_from_feature_files",
]


def _feature_source_files(root: Path, slug: str) -> tuple[str, ...]:
    status = get_feature_status(root, slug)
    paths = []
    for details in status.files.values():
        if details["exists"]:
            paths.append(str(details["path"]))
    return tuple(paths)


def _feature_missing_files(root: Path, slug: str) -> tuple[str, ...]:
    return tuple(get_feature_status(root, slug).missing_files)


def _explicit_paths_from_feature_files(root: Path, source_files: tuple[str, ...]) -> set[str]:
    paths = set()
    for relative_path in source_files:
        path = root / relative_path
        if not path.exists():
            continue
        for match in LOCAL_PATH_RE.finditer(_read_text(path)):
            paths.add(match.group("path").rstrip(".,);]`"))
    return paths
