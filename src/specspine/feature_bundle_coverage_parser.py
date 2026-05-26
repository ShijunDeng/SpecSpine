from __future__ import annotations

from pathlib import Path

from .feature_bundle_markdown import _extract_markdown_section_lines
from .feature_bundle_models import (
    CHECKBOX_TASK_RE,
    FeatureTestCoverageLink,
)
from ._coverage_link_builder import build_coverage_link

__all__ = [
    "parse_test_coverage",
]


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
        links.append(
            build_coverage_link(
                text=text,
                marker=marker,
                line_number=line_number,
                source_file=source_file,
                resolved_root=resolved_root,
                link_index=len(links),
            )
        )

    return tuple(links)
