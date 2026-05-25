from __future__ import annotations

from pathlib import Path
from typing import Any

from ..helpers import _relative_path, _normalize_lexical_path
from ._record import _artifact_record

__all__ = [
    "_include_artifact",
]


def _include_artifact(root: Path, include: str | Path) -> dict[str, Any]:
    include_value = str(include)
    include_path = Path(include)
    if include_path.is_absolute():
        candidate = include_path
    else:
        candidate = root / include_path

    display_candidate = _normalize_lexical_path(candidate)
    return _artifact_record(
        root,
        candidate,
        kind="include",
        display_path=_relative_path(root, display_candidate),
        requested_path=include_value,
    )
