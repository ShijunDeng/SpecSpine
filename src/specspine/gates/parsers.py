from __future__ import annotations

import re
from typing import Match

from .constants import (
    BULLET_RE,
    CHECKBOX_RE,
    METADATA_TAG_RE,
    QUALITY_GATE_SOURCE_FILE,
    SUPPORTED_SEVERITIES,
)
from .models import DefinitionOfDoneItem, RequiredGate

__all__ = [
    "_markdown_heading",
    "_extract_markdown_section_lines",
    "_parse_gate_metadata",
    "parse_required_checks",
    "parse_definition_of_done",
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


def _parse_gate_metadata(raw_text: str) -> tuple[
    str,
    str,
    str,
    str | None,
    dict[str, str],
    tuple[str, ...],
]:
    metadata: dict[str, str] = {}
    warnings: list[str] = []
    severity = "medium"
    owner = "unassigned"
    ci_check: str | None = None

    def replace_tag(match: Match[str]) -> str:
        nonlocal severity, owner, ci_check

        raw_key, raw_value = match.groups()
        key = raw_key.lower()
        value = raw_value.strip()
        if key not in {"severity", "owner", "ci"}:
            return match.group(0)

        if key == "severity":
            normalized = value.lower()
            metadata[key] = normalized
            if normalized in SUPPORTED_SEVERITIES:
                severity = normalized
            else:
                warnings.append(f"unsupported severity: {value}")
            return " "

        if key == "owner":
            if value:
                owner = value
                metadata[key] = value
            return " "

        if value:
            ci_check = value
            metadata[key] = value
        return " "

    cleaned_text = METADATA_TAG_RE.sub(replace_tag, raw_text).strip()
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)
    return cleaned_text, severity, owner, ci_check, metadata, tuple(warnings)


def parse_required_checks(
    content: str,
    *,
    source_file: str = QUALITY_GATE_SOURCE_FILE,
) -> tuple[RequiredGate, ...]:
    checks: list[RequiredGate] = []

    for line_number, raw_line in _extract_markdown_section_lines(
        content,
        "Required Checks",
    ):
        match = CHECKBOX_RE.match(raw_line)
        if match is None:
            continue

        marker, text = match.groups()
        (
            cleaned_text,
            severity,
            owner,
            ci_check,
            metadata,
            metadata_warnings,
        ) = _parse_gate_metadata(text.strip())
        checks.append(
            RequiredGate(
                id=f"GATE{len(checks) + 1:03d}",
                text=cleaned_text,
                done=marker.lower() == "x",
                source_file=source_file,
                line=line_number,
                severity=severity,
                owner=owner,
                ci_check=ci_check,
                metadata=metadata,
                metadata_warnings=metadata_warnings,
                raw_text=text.strip(),
            )
        )

    return tuple(checks)


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
