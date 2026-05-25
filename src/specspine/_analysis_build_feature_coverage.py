from __future__ import annotations

from pathlib import Path

from .analysis_traceability import (
    _coverage_ac_id,
    _read_test_coverage,
)

__all__ = [
    "_compute_coverage_links",
    "_compute_coverage_ids",
]


def _compute_coverage_links(root: Path, slug: str) -> list:
    return _read_test_coverage(root, slug)


def _compute_coverage_ids(
    coverage_links: list,
    known_ids: set[str],
) -> set[str]:
    return {
        _coverage_ac_id(link)
        for link in coverage_links
        if _coverage_ac_id(link) in known_ids and link.done and link.target_exists
    }
