from __future__ import annotations

from .constants import (
    BULLET_RE,
    QUALITY_GATE_SOURCE_FILE,
)
from .models import DefinitionOfDoneItem
from .heading_parser import _extract_markdown_section_lines

__all__ = [
    "parse_definition_of_done",
]


def parse_definition_of_done(
    content: str,
    *,
    source_file: str = QUALITY_GATE_SOURCE_FILE,
) -> tuple[DefinitionOfDoneItem, ...]:
    items: list[DefinitionOfDoneItem] = []

    for line_number, raw_line in _extract_markdown_section_lines(
        content,
        "Definition Of Done",
    ):
        match = BULLET_RE.match(raw_line)
        if match is None:
            continue

        text = match.group(1).strip()
        if not text:
            continue

        items.append(
            DefinitionOfDoneItem(
                id=f"DOD{len(items) + 1:03d}",
                text=text,
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(items)
