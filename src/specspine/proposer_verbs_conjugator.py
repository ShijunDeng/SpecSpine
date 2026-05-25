from __future__ import annotations

from ._verb_form_handler import (
    _get_action_verb_form,
)
from ._verb_conjugation_engine import (
    _conjugate_verb,
    _to_gerund,
    _to_past,
)
from ._verb_phonetics import (
    _is_cvc,
    _is_stressed_syllable,
)

__all__ = [
    "_get_action_verb_form",
    "_conjugate_verb",
    "_to_gerund",
    "_to_past",
    "_is_cvc",
    "_is_stressed_syllable",
]
