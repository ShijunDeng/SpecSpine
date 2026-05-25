from __future__ import annotations

from pathlib import Path

from .drift_detection_extractors import (
    _feature_peer_content,
    _extract_acs_from_spec,
)

__all__ = [
    "_extract_current_spec_acs",
]


def _extract_current_spec_acs(root: Path, slug: str):
    current = _feature_peer_content(root, slug, "spec")
    if current is None:
        return None
    return _extract_acs_from_spec(current)
