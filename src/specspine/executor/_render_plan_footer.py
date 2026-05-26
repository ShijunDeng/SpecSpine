from __future__ import annotations

from typing import Any

__all__ = [
    "_render_footer_lines",
]


def _render_footer_lines(result: dict[str, Any]) -> list[str]:
    lines: list[str] = []

    lines.extend(["", "Verification commands:"])
    for cmd in result.get("verification_commands", []):
        lines.append(f"  - {cmd}")

    rubric = result.get("grading_rubric", {})
    if rubric.get("rubric_items"):
        lines.extend([
            "",
            f"Grading rubric: {rubric.get('pass_count', 0)}/{rubric.get('total_count', 0)} pass",
        ])
        for item in rubric["rubric_items"]:
            status = item["current_status"]
            lines.append(f"  - [{status}] {item['ac_id']}: {item['ac_text']}")

    lines.extend(["", "Safety notes:"])
    for note in result.get("safety_notes", ()):
        lines.append(f"  - {note}")

    return lines
