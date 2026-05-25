from __future__ import annotations

from .workspace import normalize_template
from .proposer_build_sections import (
    _generate_why,
    _generate_scope,
    _generate_edge_cases,
    _generate_constraints,
    _generate_traceability_notes,
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
    ac_lines = "\n".join(f"- [ ] {c['id']} {c['text']}" for c in criteria)
    edge_case_lines = _generate_edge_cases(parsed)
    constraint_lines = _generate_constraints(parsed)
    traceability_lines = _generate_traceability_notes(resolved_slug, criteria)
    why_text = _generate_why(parsed, intent)

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
