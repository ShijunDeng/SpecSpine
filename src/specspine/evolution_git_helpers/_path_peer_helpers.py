from __future__ import annotations

from pathlib import Path

from ..features import feature_bundle_paths

__all__ = [
    "_get_peer_files",
    "_relative_path",
]


def _get_peer_files(slug: str, root: Path) -> dict[str, Path]:
    paths = feature_bundle_paths(root, slug)
    return {
        kind: path
        for kind, path in paths.items()
        if path.exists()
    }


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
