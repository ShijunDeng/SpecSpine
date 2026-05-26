from __future__ import annotations

from typing import Any

from ._config_scalars import _clean_config_scalar

__all__ = [
    "_parse_fusion_upstreams",
]


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
