from __future__ import annotations

from .feature_bundle_markdown_heading import _markdown_heading

__all__ = [
    "_extract_markdown_section",
    "_extract_markdown_section_lines",
]


def _extract_markdown_section(content: str, heading: str) -> str | None:
    lines = content.splitlines()
    section_start: int | None = None
    section_level: int | None = None

    for index, raw_line in enumerate(lines):
        parsed = _markdown_heading(raw_line)
        if parsed is None:
            continue

        level, text = parsed
        if section_start is None:
            if level >= 2 and text.lower() == heading.lower():
                section_start = index + 1
                section_level = level
            continue

        if section_level is not None and level <= section_level:
            section = "\n".join(lines[section_start:index]).strip()
            return section or None

    if section_start is None:
        return None

    section = "\n".join(lines[section_start:]).strip()
    return section or None


def _extract_markdown_section_lines(content: str, heading: str) -> list[tuple[int, str]]:
    lines = content.splitlines()
    section_start: int | None = None
    section_level: int | None = None

    for index, raw_line in enumerate(lines):
        parsed = _markdown_heading(raw_line)
        if parsed is None:
            continue

        level, text = parsed
        if section_start is None:
            if level >= 2 and text.lower() == heading.lower():
                section_start = index + 1
                section_level = level
            continue

        if section_level is not None and level <= section_level:
            return [
                (line_number, line)
                for line_number, line in enumerate(
                    lines[section_start:index],
                    start=section_start + 1,
                )
            ]

    if section_start is None:
        return []

    return [
        (line_number, line)
        for line_number, line in enumerate(
            lines[section_start:],
            start=section_start + 1,
        )
    ]
