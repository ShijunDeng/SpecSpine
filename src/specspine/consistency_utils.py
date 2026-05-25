from __future__ import annotations

from ._consistency_path_utils import (
    _area_prefixes,
    _candidate_files,
    _normalise_changed_file,
    _read_text,
    _relative_path,
)
from ._dedupe_utils import (
    _dedupe,
    _dedupe_references,
)

__all__ = [
    "_area_prefixes",
    "_candidate_files",
    "_dedupe",
    "_dedupe_references",
    "_normalise_changed_file",
    "_read_text",
    "_relative_path",
]
