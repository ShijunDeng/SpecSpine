from __future__ import annotations

import re

from .features import _extract_markdown_section, _extract_scalar

__all__ = [
    "_extract_title",
    "_extract_ac_summary",
    "_count_validation_evidence",
    "_determine_status_transition",
]


def _extract_title(spec_content: str) -> str:
    first_line = spec_content.splitlines()[0].strip() if spec_content.splitlines() else ""
    if first_line.startswith("# "):
        return first_line[2:].strip().strip("#").strip()
    title = _extract_scalar(spec_content, "Feature ID")
    if title:
        return title
    return ""


def _extract_ac_summary(spec_content: str, execution_content: str) -> str:
    ac_section = _extract_markdown_section(spec_content, "Acceptance Criteria")
    if ac_section:
        lines = ac_section.splitlines()
        ac_count = sum(1 for line in lines if line.strip().startswith("- ["))
        if ac_count > 0:
            return f"{ac_count} acceptance criterion/criteria defined"
    return "No acceptance criteria section found"


def _count_validation_evidence(quality_content: str) -> int:
    count = 0
    check_patterns = [
        r"- \[x\]",
        r"- \[X\]",
    ]
    for pattern in check_patterns:
        count += len(re.findall(pattern, quality_content))
    return count


def _determine_status_transition(status: str | None) -> str:
    if status is None:
        return "unknown"
    if status == "validated":
        return "newly validated"
    if status == "archived":
        return "released (archived)"
    if status == "implemented":
        return "implemented (pending validation)"
    return f"status: {status}"
