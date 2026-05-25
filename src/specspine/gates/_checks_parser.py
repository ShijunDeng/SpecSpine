from __future__ import annotations

from .constants import (
    CHECKBOX_RE,
    QUALITY_GATE_SOURCE_FILE,
)
from .models import RequiredGate
from .heading_parser import _extract_markdown_section_lines
from .metadata_parser import _parse_gate_metadata

__all__ = [
    "parse_required_checks",
]


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
