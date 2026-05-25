from __future__ import annotations

from pathlib import Path
from typing import Any


def _relative_paths(paths: list[Path], root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for path in paths)


def _clean_scalar(value: str) -> Any:
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


def _read_yaml_section(path: Path, section: str) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    return _parse_two_level_yaml_section(content, section)


__all__ = [
    "_clean_scalar",
    "_parse_two_level_yaml_section",
    "_read_yaml_section",
    "_relative_paths",
]
