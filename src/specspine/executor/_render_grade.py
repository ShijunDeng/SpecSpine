from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_grade_json",
    "render_grade_text",
]


def render_grade_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def render_grade_text(result: dict[str, Any]) -> str:
    items = result.get("rubric_items", [])
    pass_count = sum(1 for item in items if item["current_status"] == "pass")
    total = len(items)

    lines = [
        f"Grading rubric: {result['feature_id']}",
        f"Score: {pass_count}/{total} pass",
        "",
        "Rubric items:",
    ]

    for item in items:
        status = item["current_status"]
        lines.append(
            f"  - [{status}] {item['ac_id']} ({item['check_type']}): {item['ac_text']}"
        )
        if item.get("gap_reason"):
            lines.append(f"    Gap: {item['gap_reason']}")
        lines.append(f"    Criteria: {item['pass_criteria']}")

    return "\n".join(lines) + "\n"
