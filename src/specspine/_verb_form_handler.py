from __future__ import annotations

from .proposer_verbs_table import IRREGULAR_VERBS
from ._verb_conjugation_engine import _conjugate_verb  # noqa: F401

__all__ = [
    "_get_action_verb_form",
]


def _get_action_verb_form(action: str, form: str = "base") -> str:
    """Convert action verb to appropriate grammatical form."""
    if action in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[action].get(form, action)
    return _conjugate_verb(action, form)
