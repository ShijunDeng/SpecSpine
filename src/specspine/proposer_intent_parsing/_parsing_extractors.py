from __future__ import annotations

from ..proposer_intent_constants import ACTION_VERBS, MODIFIER_PREPOSITIONS, TARGET_NOUNS
from ._parsing_normalization import _normalize_to_base_form

__all__ = [
    "_build_modifier_phrase",
    "_extract_action",
    "_extract_modifiers",
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


def _extract_modifiers(text: str) -> list:
    modifiers = []
    words = text.split()
    action_words = set(ACTION_VERBS)
    i = 0
    while i < len(words):
        cleaned = words[i].strip(".,;:!?()[]{}'\"")
        if cleaned in MODIFIER_PREPOSITIONS:
            rest_words = words[i:]
            modifier_text = _build_modifier_phrase(rest_words, action_words)
            modifier = modifier_text.strip().rstrip(".")
            if modifier and modifier not in modifiers and len(modifier) > len(cleaned):
                modifiers.append(modifier)
                i += len(modifier.split())
                continue
        i += 1
    return modifiers


def _build_modifier_phrase(words: list, action_words: set) -> str:
    """Build a meaningful modifier phrase from words starting with a preposition."""
    if not words:
        return ""
    prep = words[0].strip(".,;:!?()[]{}'\"")
    phrase_words = []
    for i in range(1, len(words)):
        word = words[i].strip(".,;:!?()[]{}'\"")
        if i == 1 and word.lower() in action_words:
            break
        if word.lower() in MODIFIER_PREPOSITIONS and phrase_words:
            if len(phrase_words) >= 2:
                break
        if word.lower() in action_words and phrase_words:
            prev_word = phrase_words[-1].strip(".,;:!?()[]{}'\"").lower() if phrase_words else ""
            if prev_word not in ("the", "a", "an", "this", "that", "these", "those", "my", "your", "their", "our"):
                pass
            elif len(phrase_words) >= 2:
                break
        phrase_words.append(words[i])
    if phrase_words:
        return prep + " " + " ".join(phrase_words)
    return prep
