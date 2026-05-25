from __future__ import annotations

from pathlib import Path

from ..evolution_git_models import DiffResult
from ._diff_orchestrator import get_git_diff

__all__ = [
    "get_git_diff",
]


get_git_diff = get_git_diff
