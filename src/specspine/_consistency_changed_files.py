from __future__ import annotations

from pathlib import Path

__all__ = [
    "_normalise_changed_files",
]


def _normalise_changed_files(
    resolved_root: Path,
    changed_files: tuple[str, ...],
) -> tuple[str, ...]:
    from .consistency_utils import (
        _dedupe,
        _normalise_changed_file,
    )

    return tuple(
        _dedupe(
            [
                _normalise_changed_file(resolved_root, changed_file)
                for changed_file in changed_files
            ]
        )
    )
