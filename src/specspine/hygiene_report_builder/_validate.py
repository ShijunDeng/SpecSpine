from __future__ import annotations

from pathlib import Path

__all__ = [
    "validate_scan_root",
]


def validate_scan_root(root: Path) -> Path:
    resolved_root = root.expanduser().resolve()
    if not resolved_root.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved_root}")
    if not resolved_root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {resolved_root}")
    return resolved_root
