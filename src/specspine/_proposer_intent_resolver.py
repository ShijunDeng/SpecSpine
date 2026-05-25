from __future__ import annotations

from .proposer_intent import validate_intent, parse_intent
from .proposer_slug import _slug_to_title
from .proposer_criteria import generate_ears_criteria, generate_tasks, generate_quality_checks

__all__ = [
    "_resolve_proposal_inputs",
]


def _resolve_proposal_inputs(
    slug: str,
    intent: str,
) -> tuple:
    intent = validate_intent(intent)
    resolved_slug = slug
    title = _slug_to_title(resolved_slug)
    parsed = parse_intent(intent)
    criteria = generate_ears_criteria(parsed)
    tasks = generate_tasks(parsed, criteria)
    quality_checks = generate_quality_checks(criteria)
    return resolved_slug, title, intent, parsed, criteria, tasks, quality_checks
