from __future__ import annotations

from pathlib import Path


def _source_snapshot_path(kind: str) -> Path:
    return Path("sources") / f"{kind}.md"


__all__ = [
    "_source_snapshot_path",
]
