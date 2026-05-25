from __future__ import annotations

from typing import Any

__all__ = [
    "_determine_ac_status",
]


def _determine_ac_status(
    ac_done: bool,
    ac_coverage: list[dict[str, Any]],
) -> tuple[str, str]:
    coverage_complete = any(
        c["done"] and c["target_exists"] for c in ac_coverage
    ) if ac_coverage else False
    has_any_valid_coverage = any(
        c["target_exists"] for c in ac_coverage
    ) if ac_coverage else False

    if ac_done and coverage_complete:
        status = "pass"
    elif ac_done and has_any_valid_coverage:
        status = "warn"
    elif ac_done:
        status = "fail"
    elif coverage_complete:
        status = "warn"
    elif has_any_valid_coverage:
        status = "warn"
    else:
        status = "fail"

    gap_reason = ""
    if status == "fail":
        gap_reason = "No test coverage links found for this AC."
    elif status == "warn":
        gap_reason = "Coverage links exist but are incomplete or unchecked."

    return status, gap_reason
