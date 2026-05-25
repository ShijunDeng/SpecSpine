from __future__ import annotations

from typing import Any

__all__ = [
    "_determine_ac_status",
    "_build_ac_rubric_item",
    "_build_quality_rubric_item",
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


def _build_ac_rubric_item(
    ac_id: str,
    ac_text: str,
    status: str,
    gap_reason: str,
) -> dict[str, Any]:
    return {
        "ac_id": ac_id,
        "ac_text": ac_text,
        "check_type": "acceptance_criterion",
        "pass_criteria": f"AC {ac_id} is checked and has at least one completed test coverage link.",
        "current_status": status,
        "gap_reason": gap_reason,
    }


def _build_quality_rubric_item(
    quality_checks_total: int,
    quality_checks_done: int,
) -> dict[str, Any] | None:
    if quality_checks_total == 0:
        return None

    q_status = "pass" if quality_checks_done == quality_checks_total else "warn"
    return {
        "ac_id": "QUALITY_CHECKS",
        "ac_text": f"{quality_checks_done}/{quality_checks_total} quality checks done",
        "check_type": "quality_gates",
        "pass_criteria": "All required quality checks must be completed.",
        "current_status": q_status,
        "gap_reason": "" if q_status == "pass" else f"{quality_checks_total - quality_checks_done} quality checks remain open.",
    }
