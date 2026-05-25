from __future__ import annotations

from ._checklist_core import _parse_trace_checklist_items

__all__ = [
    "parse_acceptance_criteria",
    "parse_quality_checks",
    "parse_release_readiness",
]


def parse_acceptance_criteria(
    content: str,
    *,
    source_file: str,
) -> tuple["FeatureTraceChecklistItem", ...]:
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
) -> tuple["FeatureTraceChecklistItem", ...]:
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
) -> tuple["FeatureTraceChecklistItem", ...]:
    return _parse_trace_checklist_items(
        content,
        heading="Release Readiness",
        prefix="RR",
        source_file=source_file,
    )
