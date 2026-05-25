from __future__ import annotations

import re
from pathlib import Path

from ..dependency import (
    EXPLICIT_DEP_PATTERNS,
)

__all__ = [
    "_extract_acceptance_criteria",
    "_extract_slugs_from_text",
    "_find_referenced_acs",
]


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
