from __future__ import annotations

from pathlib import Path
from typing import Any

from ._section_parsing import _parse_two_level_yaml_section

__all__ = ["_read_yaml_section"]


def _read_yaml_section(path: Path, section: str) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    return _parse_two_level_yaml_section(content, section)
