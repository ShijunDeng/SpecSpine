from __future__ import annotations

from ..proposer_intent_constants import ACTION_VERBS, MODIFIER_PREPOSITIONS

__all__ = [
    "_build_modifier_phrase",
    "_extract_modifiers",
]


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
