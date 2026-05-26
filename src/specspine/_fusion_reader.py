from __future__ import annotations

from pathlib import Path
from typing import Any

from ._fusion_parser import _parse_fusion_upstreams

__all__ = [
    "_read_fusion_upstreams",
]


def _read_fusion_upstreams(root: Path) -> dict[str, dict[str, Any]]:
    fusion_path = root / ".specspine" / "fusion.yaml"
    if not fusion_path.exists():
        return {}

    try:
        return _parse_fusion_upstreams(fusion_path.read_text(encoding="utf-8"))
    except OSError:
        return {}
