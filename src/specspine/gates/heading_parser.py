from __future__ import annotations

__all__ = [
    "_markdown_heading",
    "_extract_markdown_section_lines",
]


def _markdown_heading(raw_line: str) -> tuple[int, str] | None:
    stripped = raw_line.strip()
    if not stripped.startswith("#"):
        return None

    marks = len(stripped) - len(stripped.lstrip("#"))
    if marks == 0 or marks > 6:
        return None

    if len(stripped) == marks or stripped[marks] != " ":
        return None

    return marks, stripped[marks:].strip()


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
            if level == 2 and text.lower() == heading.lower():
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
