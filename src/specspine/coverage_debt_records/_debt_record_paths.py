from __future__ import annotations

from ..features import FEATURE_FILE_PATHS, feature_bundle_paths

__all__ = [
    "_resolve_feature_paths",
]


def _resolve_feature_paths(slug: str, root):
    paths = feature_bundle_paths(root, slug)
    relative_paths = {
        kind: relative_path.format(slug=slug)
        for kind, relative_path in FEATURE_FILE_PATHS.items()
    }
    return paths, relative_paths
