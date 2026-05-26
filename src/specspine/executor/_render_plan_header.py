from __future__ import annotations

from typing import Any

__all__ = [
    "_render_plan_header_lines",
]


def _render_plan_header_lines(result: dict[str, Any]) -> list[str]:
    return [
        f"Execution plan: {result['feature_id']}",
        f"Status: {result['feature_status']}",
        "",
        f"Summary: "
        f"steps={result['summary']['total_steps']} "
        f"blocked={result['summary']['blocked_steps']} "
        f"completed={result['summary']['completed_steps']} "
        f"ac={result['summary']['acceptance_criteria']}",
        "",
        "Dependency order: " + " -> ".join(result["dependency_order"]) if result["dependency_order"] else "Dependency order: (none)",
        "",
        "Steps:",
    ]
