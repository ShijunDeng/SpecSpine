from __future__ import annotations

from typing import Any

from ._scalar_cleaning import _clean_scalar

__all__ = ["_parse_two_level_yaml_section"]


def _parse_two_level_yaml_section(content: str, section: str) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    in_section = False
    current_key: str | None = None

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            in_section = stripped == f"{section}:"
            current_key = None
            continue

        if not in_section:
            continue

        if indent == 2 and stripped.endswith(":"):
            current_key = stripped[:-1]
            values.setdefault(current_key, {})
            continue

        if indent == 4 and current_key and ":" in stripped:
            key, value = stripped.split(":", 1)
            values[current_key][key.strip()] = _clean_scalar(value)

    return values
