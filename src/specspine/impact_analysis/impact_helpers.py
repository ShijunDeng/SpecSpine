from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..dependency import (
    EXPLICIT_DEP_PATTERNS,
    _list_feature_slugs,
    _read_all_feature_content,
)

__all__ = [
    "_extract_acceptance_criteria",
    "_extract_slugs_from_text",
    "_find_referenced_acs",
    "_find_slug_symbols",
    "_module_name",
    "_read_text",
    "_relative_path",
]


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _extract_acceptance_criteria(content: str) -> list[tuple[str, str]]:
    criteria: list[tuple[str, str]] = []
    in_section = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("## acceptance criteria"):
            in_section = True
            continue
        if in_section:
            if stripped.startswith("## "):
                break
            match = re.match(r"- \[[ xX]\]\s+(.+)", stripped)
            if match:
                criteria.append(("", match.group(1)))
            match_ac = re.match(r"- \[[ xX]\]\s*(AC\d+)\s*[-:]\s*(.*)", stripped)
            if match_ac:
                criteria[-1] = (match_ac.group(1), match_ac.group(2)) if criteria else (match_ac.group(1), match_ac.group(2))
    return criteria


def _extract_slugs_from_text(
    text: str,
    current_slug: str,
    valid_slugs: set[str] | None = None,
) -> list[str]:
    slugs: list[str] = []
    for pattern in EXPLICIT_DEP_PATTERNS:
        for match in pattern.finditer(text):
            found = match.group(1)
            if found != current_slug and found not in slugs:
                if valid_slugs is None or found in valid_slugs:
                    slugs.append(found)
    return slugs


def _find_referenced_acs(
    content: str,
    slug: str,
    root: Path,
) -> tuple[str, ...]:
    acs: list[str] = []
    for match in re.finditer(r"(AC\d+)", content):
        ac_id = match.group(1)
        if ac_id not in acs:
            acs.append(ac_id)
    return tuple(acs)


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
