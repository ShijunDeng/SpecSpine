from __future__ import annotations

from ._sections_planning import (
    _generate_dependencies,
    _generate_open_questions,
    _generate_test_plan,
    _generate_traceability_notes,
)
from ._sections_spec import (
    _generate_constraints,
    _generate_edge_cases,
    _generate_scope,
    _generate_why,
)

__all__ = [
    "_generate_constraints",
    "_generate_dependencies",
    "_generate_edge_cases",
    "_generate_open_questions",
    "_generate_scope",
    "_generate_test_plan",
    "_generate_traceability_notes",
    "_generate_why",
]

_generate_constraints = _generate_constraints
_generate_dependencies = _generate_dependencies
_generate_edge_cases = _generate_edge_cases
_generate_open_questions = _generate_open_questions
_generate_scope = _generate_scope
_generate_test_plan = _generate_test_plan
_generate_traceability_notes = _generate_traceability_notes
_generate_why = _generate_why
