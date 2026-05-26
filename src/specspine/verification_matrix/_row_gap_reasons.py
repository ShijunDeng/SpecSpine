from __future__ import annotations

from typing import Any

__all__ = [
    "_row_gap_reasons",
]


def _row_gap_reasons(
    *,
    criterion_done: bool,
    coverage_links: list[dict[str, Any]],
    coverage_complete: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not criterion_done:
        reasons.append("acceptance_criterion_open")
    if not coverage_links:
        reasons.append("missing_test_coverage")
    elif not coverage_complete:
        reasons.append("test_coverage_incomplete")
    return tuple(reasons)
