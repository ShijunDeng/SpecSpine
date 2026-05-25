from __future__ import annotations

from ..proposer_intent_constants import ACTION_VERBS, MODIFIER_PREPOSITIONS, TARGET_NOUNS
from ._parsing_normalization import _normalize_to_base_form

__all__ = [
    "_extract_action",
    "_extract_target",
]


def _extract_action(text: str) -> str:
    words = text.split()
    for word in words:
        cleaned = word.strip(".,;:!?()[]{}'\"")
        if cleaned in ACTION_VERBS:
            return cleaned
    return "implement"


def _extract_target(text: str) -> str:
    words = text.split()
    found_nouns = []
    preposition_nouns = []
    in_preposition_phrase = False
    for i, word in enumerate(words):
        cleaned = word.strip(".,;:!?()[]{}'\"")
        normalized = _normalize_to_base_form(cleaned)
        if normalized in TARGET_NOUNS:
            if in_preposition_phrase:
                preposition_nouns.append(normalized)
            else:
                found_nouns.append(normalized)
        if cleaned in MODIFIER_PREPOSITIONS:
            in_preposition_phrase = True
        elif cleaned not in ("and", "or", "but", "the", "a", "an", "this", "that"):
            if i > 0 and words[i-1].strip(".,;:!?()[]{}'\"") not in MODIFIER_PREPOSITIONS:
                in_preposition_phrase = False
    if found_nouns:
        return found_nouns[-1]
    if preposition_nouns:
        return preposition_nouns[0]
    return "feature"
