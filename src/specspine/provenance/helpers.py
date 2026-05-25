from __future__ import annotations

import hashlib
import os
from pathlib import Path

__all__ = [
    "CHUNK_SIZE",
    "PathLike",
    "_is_within_root",
    "_resolve_path",
    "_relative_path",
    "_normalize_lexical_path",
    "_hash_file",
]

CHUNK_SIZE = 1024 * 1024
PathLike = str | Path


def _is_within_root(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _resolve_path(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except (OSError, RuntimeError):
        return path.absolute()


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _normalize_lexical_path(path: Path) -> Path:
    return Path(os.path.normpath(str(path)))


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()
