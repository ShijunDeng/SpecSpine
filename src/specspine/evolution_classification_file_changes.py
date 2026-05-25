from __future__ import annotations

from .evolution_classification_file_changes_added import (
    _classify_added_file,
)
from .evolution_classification_file_changes_removed import (
    _classify_removed_file,
)

__all__ = [
    "_classify_added_file",
    "_classify_removed_file",
]

_classify_added_file = _classify_added_file
_classify_removed_file = _classify_removed_file
