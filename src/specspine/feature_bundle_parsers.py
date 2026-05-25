from __future__ import annotations

from pathlib import Path

from .feature_bundle_markdown import _extract_markdown_section_lines
from .feature_bundle_models import (
    AC_ID_RE,
    CHECKBOX_TASK_RE,
    FeatureAcceptanceTestCase,
    FeatureTask,
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
)

__all__ = [
    "parse_acceptance_criteria",
    "parse_feature_tasks",
    "parse_quality_checks",
    "parse_test_coverage",
    "parse_test_plan",
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


def parse_feature_tasks(
    content: str,
    *,
    source_file: str,
) -> tuple[FeatureTask, ...]:
    tasks: list[FeatureTask] = []

    for line_number, raw_line in _extract_markdown_section_lines(content, "Tasks"):
        match = CHECKBOX_TASK_RE.match(raw_line)
        if match is None:
            continue

        task_id = f"T{len(tasks) + 1:03d}"
        marker, text = match.groups()
        tasks.append(
            FeatureTask(
                id=task_id,
                text=text.strip(),
                done=marker.lower() == "x",
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(tasks)


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


def _strip_markdown_code(text: str) -> str:
    stripped = text.strip()
    if len(stripped) >= 2 and stripped.startswith("`") and stripped.endswith("`"):
        return stripped[1:-1].strip()
    return stripped


def _test_coverage_target_path(target: str) -> str:
    return _strip_markdown_code(target).split("::", 1)[0].strip()


def parse_test_coverage(
    content: str,
    *,
    source_file: str,
    root: Path,
) -> tuple[FeatureTestCoverageLink, ...]:
    links: list[FeatureTestCoverageLink] = []
    resolved_root = root.expanduser().resolve()

    for line_number, raw_line in _extract_markdown_section_lines(content, "Test Coverage"):
        match = CHECKBOX_TASK_RE.match(raw_line)
        if match is None:
            continue

        marker, text = match.groups()
        normalized_text = text.strip()
        ac_match = AC_ID_RE.search(normalized_text)
        acceptance_criterion_id = (
            ac_match.group(0).upper() if ac_match is not None else "unknown"
        )
        target = ""
        if "->" in normalized_text:
            _left, right = normalized_text.split("->", 1)
            target = _strip_markdown_code(right)
        target_path = _test_coverage_target_path(target)
        target_path_obj = Path(target_path)
        target_exists = (
            bool(target_path)
            and not target_path_obj.is_absolute()
            and (resolved_root / target_path_obj).exists()
        )
        links.append(
            FeatureTestCoverageLink(
                id=f"COV{len(links) + 1:03d}",
                acceptance_criterion_id=acceptance_criterion_id,
                target=target,
                target_path=target_path,
                target_exists=target_exists,
                done=marker.lower() == "x",
                text=normalized_text,
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(links)


def parse_test_plan(
    content: str,
    *,
    source_file: str,
) -> tuple[FeatureTraceTestPlanItem, ...]:
    items: list[FeatureTraceTestPlanItem] = []

    for line_number, raw_line in _extract_markdown_section_lines(content, "Test Plan"):
        text = raw_line.strip()
        if not text:
            continue

        items.append(
            FeatureTraceTestPlanItem(
                id=f"TP{len(items) + 1:03d}",
                text=text,
                source_file=source_file,
                line=line_number,
            )
        )

    return tuple(items)


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
