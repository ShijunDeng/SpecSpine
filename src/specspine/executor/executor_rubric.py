from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    parse_acceptance_criteria,
    parse_quality_checks,
    parse_test_coverage,
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
    spec_content = contents.get("spec", "")
    quality_content = contents.get("quality", "")

    ac_items = parse_acceptance_criteria(spec_content, source_file=relative_paths.get("spec", "")) if spec_content else ()
    coverage_links = parse_test_coverage(quality_content, source_file=relative_paths.get("quality", ""), root=root) if quality_content else ()
    quality_items = parse_quality_checks(quality_content, source_file=relative_paths.get("quality", "")) if quality_content else ()

    coverage_by_ac: dict[str, list[dict[str, Any]]] = {}
    for link in coverage_links:
        coverage_by_ac.setdefault(link.acceptance_criterion_id, []).append({
            "done": link.done,
            "target_exists": link.target_exists,
            "target_path": link.target_path,
        })

    quality_by_ac: dict[str, list[dict[str, Any]]] = {}
    for item in quality_items:
        quality_by_ac.setdefault("all", []).append({
            "id": item.id,
            "done": item.done,
            "text": item.text,
        })

    rubric_items: list[dict[str, Any]] = []
    for ac in ac_items:
        ac_coverage = coverage_by_ac.get(ac.id, [])
        coverage_complete = any(
            c["done"] and c["target_exists"] for c in ac_coverage
        ) if ac_coverage else False
        has_any_valid_coverage = any(
            c["target_exists"] for c in ac_coverage
        ) if ac_coverage else False

        if ac.done and coverage_complete:
            status = "pass"
        elif ac.done and has_any_valid_coverage:
            status = "warn"
        elif ac.done:
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

        rubric_items.append({
            "ac_id": ac.id,
            "ac_text": ac.text,
            "check_type": "acceptance_criterion",
            "pass_criteria": f"AC {ac.id} is checked and has at least one completed test coverage link.",
            "current_status": status,
            "gap_reason": gap_reason,
        })

    quality_checks_total = len(quality_items)
    quality_checks_done = sum(1 for item in quality_items if item.done)

    if quality_checks_total > 0:
        q_status = "pass" if quality_checks_done == quality_checks_total else "warn"
        rubric_items.append({
            "ac_id": "QUALITY_CHECKS",
            "ac_text": f"{quality_checks_done}/{quality_checks_total} quality checks done",
            "check_type": "quality_gates",
            "pass_criteria": "All required quality checks must be completed.",
            "current_status": q_status,
            "gap_reason": "" if q_status == "pass" else f"{quality_checks_total - quality_checks_done} quality checks remain open.",
        })

    return rubric_items
