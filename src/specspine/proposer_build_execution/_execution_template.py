from __future__ import annotations

from ..workspace import normalize_template
from ..proposer_build_sections import (
    _generate_why,
    _generate_dependencies,
    _generate_open_questions,
)
from ._execution_task_formatting import _format_task_lines


def build_execution_header(
    resolved_slug: str,
    title: str,
    parsed: dict,
    tasks: list[dict],
    intent: str,
) -> str:
    why_text = _generate_why(parsed, intent)
    task_lines = _format_task_lines(tasks)
    dependency_lines = _generate_dependencies(parsed)
    open_questions_line = _generate_open_questions(parsed)

    action = parsed.get("action", "feature")

    return normalize_template(f"""
# {title} Execution

Feature ID: {resolved_slug}
Status: proposed
Why: {why_text}

## Milestones

- M1: Module scaffolding and file structure in place
- M2: Core {action} logic implemented for all acceptance criteria
- M3: CLI integration and validation complete
- M4: Tests written and passing, documentation updated

## Tasks

{task_lines}

## Dependencies

{dependency_lines}

## Open Questions

{open_questions_line}
""")


__all__ = [
    "build_execution_header",
]
