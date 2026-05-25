from __future__ import annotations

from pathlib import Path

from ..features import (
    feature_bundle_paths,
)

__all__ = [
    "_resolve_feature_paths",
]


def _resolve_feature_paths(root: Path, slug: str) -> list[str]:
    peer_files = feature_bundle_paths(root, slug)
    if not peer_files:
        return []

    rel_paths = []
    for kind in ("spec", "execution", "quality"):
        p = peer_files.get(kind)
        if p is not None and p.exists():
            try:
                rel_paths.append(str(p.relative_to(root)))
            except ValueError:
                pass

    return rel_paths
