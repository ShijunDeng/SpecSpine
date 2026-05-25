from __future__ import annotations

from .proposer_build_sections import (
    _generate_why,
    _generate_edge_cases,
    _generate_constraints,
    _generate_traceability_notes,
)

__all__ = [
    "_generate_ac_lines",
    "_generate_why_text",
    "_generate_edge_case_lines",
    "_generate_constraint_lines",
    "_generate_traceability_lines",
]


def _generate_ac_lines(criteria: list[dict]) -> str:
    return "\n".join(f"- [ ] {c['id']} {c['text']}" for c in criteria)


def _generate_why_text(parsed: dict, intent: str) -> str:
    return _generate_why(parsed, intent)


def _generate_edge_case_lines(parsed: dict) -> str:
    return _generate_edge_cases(parsed)


def _generate_constraint_lines(parsed: dict) -> str:
    return _generate_constraints(parsed)


def _generate_traceability_lines(resolved_slug: str, criteria: list[dict]) -> str:
    return _generate_traceability_notes(resolved_slug, criteria)
