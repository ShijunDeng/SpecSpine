from __future__ import annotations

from .workspace import normalize_template
from .proposer_build_sections import _generate_scope
from ._spec_section_content import (
    _generate_ac_lines,
    _generate_why_text,
    _generate_edge_case_lines,
    _generate_constraint_lines,
    _generate_traceability_lines,
)

__all__ = [
    "build_spec_content",
]


def build_spec_content(
    resolved_slug: str,
    title: str,
    parsed: dict,
    criteria: list[dict],
    priority: str,
    owner: str,
    milestone: str,
    target_release: str,
    project: str,
    effort: str,
    intent: str,
) -> str:
    ac_lines = _generate_ac_lines(criteria)
    edge_case_lines = _generate_edge_case_lines(parsed)
    constraint_lines = _generate_constraint_lines(parsed)
    traceability_lines = _generate_traceability_lines(resolved_slug, criteria)
    why_text = _generate_why_text(parsed, intent)

    return normalize_template(f"""
# {title}

Feature ID: {resolved_slug}
Status: proposed
Priority: {priority}
Owner: {owner}
Milestone: {milestone}
Target Release: {target_release}
Project: {project}
Effort: {effort}

## Why

{why_text}

## Users

- End users who need to {parsed['action']} the {parsed['target']}
- Developers maintaining the {parsed['target']} functionality
- Operators configuring the {parsed['target']} in production

## Scope

- {_generate_scope(parsed)}
- Support for {parsed['action']}ing the {parsed['target']} in all relevant contexts
- Integration with existing system components

## Non-Goals

- This feature will not modify unrelated system behavior
- Migration of existing data is out of scope unless explicitly required
- Third-party integrations beyond core functionality

## Acceptance Criteria

{ac_lines}

## Edge Cases

{edge_case_lines}

## Constraints

{constraint_lines}

## Traceability Notes

{traceability_lines}
""")
