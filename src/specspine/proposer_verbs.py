from __future__ import annotations

from .proposer_verbs_table import IRREGULAR_VERBS
from .proposer_verbs_conjugator import (
    _conjugate_verb,
    _get_action_verb_form,
    _is_cvc,
    _is_stressed_syllable,
    _to_gerund,
    _to_past,
)

__all__ = [
    "IRREGULAR_VERBS",
    "_get_action_verb_form",
    "_conjugate_verb",
    "_to_gerund",
    "_to_past",
    "_is_cvc",
    "_is_stressed_syllable",
]
