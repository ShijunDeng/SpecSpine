from __future__ import annotations

from pathlib import Path

from .audit_models import AuditEvent
from .features import FEATURE_FILE_PATHS
from .consistency import _read_text

__all__ = [
    "_feature_peer_content",
]


def _feature_peer_content(root: Path, slug: str, kind: str) -> str | None:
    rel_path = FEATURE_FILE_PATHS.get(kind)
    if rel_path is None:
        return None
    path = root / rel_path.format(slug=slug)
    if not path.exists():
        return None
    return _read_text(path)
