from __future__ import annotations

from ._evolution_git_diff import get_git_diff
from ._evolution_git_versioned_content import _build_versioned_content

__all__ = [
    "get_git_diff",
    "_build_versioned_content",
]
