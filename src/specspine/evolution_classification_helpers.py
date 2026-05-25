from __future__ import annotations

import re

from .evolution_classification_models import AC_ID_RE, TASK_ID_RE

__all__ = [
    "_extract_ac_ids",
    "_extract_task_ids",
    "_find_line_number",
    "_parse_section_ids",
    "_extract_metadata",
]


def _extract_ac_ids(text: str) -> list[str]:
    return AC_ID_RE.findall(text)


def _extract_task_ids(text: str) -> list[str]:
    return TASK_ID_RE.findall(text)


def _find_line_number(content: str, search_text: str) -> int:
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        if search_text.strip() in line:
            return i
    return 0


def _parse_section_ids(content: str, pattern: re.Pattern) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    for i, line in enumerate(content.splitlines(), 1):
        for match in pattern.finditer(line):
            results.append((match.group(1), i))
    return results


def _extract_metadata(content: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    keys = {"Priority", "Owner", "Milestone", "Target Release", "Project", "Effort", "Status"}
    for line in content.splitlines():
        stripped = line.strip()
        if ":" in stripped and not stripped.startswith("#"):
            key, _, value = stripped.partition(":")
            key = key.strip()
            if key in keys:
                metadata[key] = value.strip()
    return metadata
