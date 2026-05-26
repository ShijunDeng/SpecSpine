from __future__ import annotations

from ._critical_path_core import _compute_critical_path
from ._critical_path_builder import compute_critical_path

__all__ = [
    "_compute_critical_path",
    "compute_critical_path",
]
