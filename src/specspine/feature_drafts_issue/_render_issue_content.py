from __future__ import annotations

__all__ = [
    "_render_issue_content",
]


def _render_issue_content(
    *,
    why: str,
    acceptance_criteria: str,
    tasks: str,
    test_plan: str,
) -> list[str]:
    return [
        "## Why",
        "",
        why,
        "",
        "## Acceptance Criteria",
        "",
        acceptance_criteria,
        "",
        "## Tasks",
        "",
        tasks,
        "",
        "## Test Plan",
        "",
        test_plan,
        "",
    ]
