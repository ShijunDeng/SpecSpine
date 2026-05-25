from __future__ import annotations

from pathlib import Path

from .features import feature_bundle_paths

__all__ = [
    "_resolve_audit_event_paths",
]


def _resolve_audit_event_paths(slug: str, root: Path) -> tuple[list[str], bool]:
    """Resolve feature bundle paths to git-tracked relative paths.

    Returns (rel_paths, has_files) where rel_paths are relative path strings
    suitable for git log arguments.
    """
    peer_files = feature_bundle_paths(root, slug)
    if not peer_files:
        return [], False

    rel_paths: list[str] = []
    for kind in ("spec", "execution", "quality"):
        p = peer_files.get(kind)
        if p is not None and p.exists():
            try:
                rel_paths.append(str(p.relative_to(root)))
            except ValueError:
                pass

    return rel_paths, bool(rel_paths)
