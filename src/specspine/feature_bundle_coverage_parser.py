from __future__ import annotations

from pathlib import Path

from .feature_bundle_markdown import _extract_markdown_section_lines
from .feature_bundle_models import (
    AC_ID_RE,
    CHECKBOX_TASK_RE,
    FeatureTestCoverageLink,
)
from .feature_bundle_coverage_helpers import (
    _strip_markdown_code,
    _test_coverage_target_path,
)

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
