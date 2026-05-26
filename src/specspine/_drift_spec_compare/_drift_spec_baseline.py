from __future__ import annotations

from pathlib import Path
from typing import Any

from ..drift_detection_extractors import (
    _baseline_peer_content,
    _extract_acs_from_spec,
)

__all__ = [
    "_read_baseline_spec",
    "_extract_baseline_acs",
]


def _read_baseline_spec(
    root: Path,
    slug: str,
    baseline: str,
) -> str | None:
    return _baseline_peer_content(root, slug, "spec", baseline)


def _extract_baseline_acs(content: str) -> list[str]:
    return _extract_acs_from_spec(content)
