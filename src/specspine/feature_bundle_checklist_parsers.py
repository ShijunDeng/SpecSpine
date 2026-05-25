from __future__ import annotations

from .feature_bundle_markdown import _extract_markdown_section_lines
from .feature_bundle_models import (
    CHECKBOX_TASK_RE,
    FeatureTraceChecklistItem,
)

__all__ = [
    "_parse_trace_checklist_items",
    "parse_acceptance_criteria",
    "parse_quality_checks",
    "parse_release_readiness",
]


def _parse_trace_checklist_items(
    content: str,
    *,
    heading: str,
    prefix: str,
    source_file: str,
) -> tuple[FeatureTraceChecklistItem, ...]:
    items: list[FeatureTraceChecklistItem] = []

    for line_number, raw_line in _extract_markdown_section_lines(content, heading):
        match = CHECKBOX_TASK_RE.match(raw_line)
        if match is None:
            continue

        marker, text = match.groups()
        items.append(
            FeatureTraceChecklistItem(
                id=f"{prefix}{len(items) + 1:03d}",
                text=text.strip(),
                done=marker.lower() == "x",
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(items)


def parse_acceptance_criteria(
    content: str,
    *,
    source_file: str,
) -> tuple[FeatureTraceChecklistItem, ...]:
    return _parse_trace_checklist_items(
        content,
        heading="Acceptance Criteria",
        prefix="AC",
        source_file=source_file,
    )


def parse_quality_checks(
    content: str,
    *,
    source_file: str,
) -> tuple[FeatureTraceChecklistItem, ...]:
    return _parse_trace_checklist_items(
        content,
        heading="Required Checks",
        prefix="Q",
        source_file=source_file,
    )


def parse_release_readiness(
    content: str,
    *,
    source_file: str,
) -> tuple[FeatureTraceChecklistItem, ...]:
    return _parse_trace_checklist_items(
        content,
        heading="Release Readiness",
        prefix="RR",
        source_file=source_file,
    )
