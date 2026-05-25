from __future__ import annotations

from pathlib import Path

from ..features import validate_feature_slug
from ..evolution_git_models import DiffResult
from ..evolution_git_helpers import _get_peer_files
from ._diff_file_processor import _process_file_diff

__all__ = [
    "get_git_diff",
]


def get_git_diff(
    slug: str,
    root: Path,
    base: str | None = None,
    unstaged: bool = False,
) -> DiffResult:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    peer_files = _get_peer_files(slug, resolved_root)

    if not peer_files:
        return DiffResult(slug=slug, files=[])

    file_results = []
    for kind, file_path in sorted(peer_files.items()):
        file_results.append(
            _process_file_diff(
                file_path,
                resolved_root,
                base=base,
                unstaged=unstaged,
            )
        )

    return DiffResult(slug=slug, files=file_results)
