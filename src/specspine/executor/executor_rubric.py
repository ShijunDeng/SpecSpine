from __future__ import annotations

from pathlib import Path
from typing import Any

from ._rubric_parsing import (
    _parse_rubric_inputs,
    _build_coverage_by_ac,
    _build_quality_by_ac,
)
from ._rubric_scoring import (
    _determine_ac_status,
    _build_ac_rubric_item,
    _build_quality_rubric_item,
)

__all__ = [
    "_build_grading_rubric_internal",
]


def _build_grading_rubric_internal(
    contents: dict[str, str],
    slug: str,
    root: Path,
    relative_paths: dict[str, str],
) -> list[dict[str, Any]]:
    ac_items, coverage_links, quality_items = _parse_rubric_inputs(
        contents, slug, root, relative_paths,
    )

    coverage_by_ac = _build_coverage_by_ac(coverage_links)
    quality_by_ac = _build_quality_by_ac(quality_items)

    rubric_items: list[dict[str, Any]] = []
    for ac in ac_items:
        ac_coverage = coverage_by_ac.get(ac.id, [])
        status, gap_reason = _determine_ac_status(ac.done, ac_coverage)

        rubric_items.append(
            _build_ac_rubric_item(ac.id, ac.text, status, gap_reason),
        )

    quality_checks_total = len(quality_items)
    quality_checks_done = sum(1 for item in quality_items if item.done)

    quality_item = _build_quality_rubric_item(quality_checks_total, quality_checks_done)
    if quality_item is not None:
        rubric_items.append(quality_item)

    return rubric_items
