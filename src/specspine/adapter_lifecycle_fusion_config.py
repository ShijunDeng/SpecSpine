from __future__ import annotations

from pathlib import Path
from typing import Any

__all__ = [
    "_clean_config_scalar",
    "_parse_fusion_upstreams",
    "_read_fusion_upstreams",
]


def _clean_config_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _parse_fusion_upstreams(content: str) -> dict[str, dict[str, Any]]:
    upstreams: dict[str, dict[str, Any]] = {}
    in_upstreams = False
    current_key: str | None = None

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            in_upstreams = stripped == "upstreams:"
            current_key = None
            continue

        if not in_upstreams:
            continue

        if indent == 2 and stripped.endswith(":"):
            current_key = stripped[:-1]
            upstreams.setdefault(current_key, {})
            continue

        if indent == 4 and current_key and ":" in stripped:
            key, value = stripped.split(":", 1)
            upstreams[current_key][key.strip()] = _clean_config_scalar(value)

    return upstreams


def _read_fusion_upstreams(root: Path) -> dict[str, dict[str, Any]]:
    fusion_path = root / ".specspine" / "fusion.yaml"
    if not fusion_path.exists():
        return {}

    try:
        return _parse_fusion_upstreams(fusion_path.read_text(encoding="utf-8"))
    except OSError:
        return {}
