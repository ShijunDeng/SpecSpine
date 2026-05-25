from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    parse_acceptance_criteria,
    parse_quality_checks,
    parse_test_coverage,
)

__all__ = [
    "_parse_rubric_inputs",
    "_build_coverage_by_ac",
    "_build_quality_by_ac",
]


def _parse_rubric_inputs(
    contents: dict[str, str],
    slug: str,
    root: Path,
    relative_paths: dict[str, str],
) -> tuple:
    spec_content = contents.get("spec", "")
    quality_content = contents.get("quality", "")

    ac_items = parse_acceptance_criteria(spec_content, source_file=relative_paths.get("spec", "")) if spec_content else ()
    coverage_links = parse_test_coverage(quality_content, source_file=relative_paths.get("quality", ""), root=root) if quality_content else ()
    quality_items = parse_quality_checks(quality_content, source_file=relative_paths.get("quality", "")) if quality_content else ()

    return ac_items, coverage_links, quality_items


def _build_coverage_by_ac(coverage_links) -> dict[str, list[dict[str, Any]]]:
    coverage_by_ac: dict[str, list[dict[str, Any]]] = {}
    for link in coverage_links:
        coverage_by_ac.setdefault(link.acceptance_criterion_id, []).append({
            "done": link.done,
            "target_exists": link.target_exists,
            "target_path": link.target_path,
        })
    return coverage_by_ac


def _build_quality_by_ac(quality_items) -> dict[str, list[dict[str, Any]]]:
    quality_by_ac: dict[str, list[dict[str, Any]]] = {}
    for item in quality_items:
        quality_by_ac.setdefault("all", []).append({
            "id": item.id,
            "done": item.done,
            "text": item.text,
        })
    return quality_by_ac
