from __future__ import annotations

import re
from pathlib import Path

from ._helpers_path import _relative_path

__all__ = [
    "_module_name",
    "_find_slug_symbols",
]


def _module_name(source_file: Path, root: Path) -> str:
    rel = _relative_path(root, source_file)
    if rel.endswith(".py"):
        rel = rel[:-3]
    return rel.replace("/", ".")


def _find_slug_symbols(content: str, slug: str) -> tuple[str, ...]:
    symbols: list[str] = []
    for line in content.splitlines():
        if slug in line:
            for match in re.finditer(r"(?:def|class)\s+(\w+)", line):
                sym = match.group(1)
                if sym not in symbols:
                    symbols.append(sym)
    return tuple(sorted(symbols))
