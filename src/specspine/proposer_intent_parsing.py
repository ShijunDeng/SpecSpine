from __future__ import annotations

from .proposer_intent_constants import (
    ACTION_VERBS,
    MODIFIER_PREPOSITIONS,
    TARGET_NOUNS,
)
from .proposer_intent_validation import validate_intent


def parse_intent(intent: str) -> dict:
    text = validate_intent(intent).lower()

    from .proposer_intent_constants import COMPONENT_SPLITTERS
    raw_components = COMPONENT_SPLITTERS.split(text)
    components = [c.strip() for c in raw_components if c.strip()]
    is_complex = len(components) > 1

    if is_complex:
        primary = components[0]
    else:
        primary = text

    action = _extract_action(primary)
    target = _extract_target(primary)
    modifiers = _extract_modifiers(primary)

    return {
        "action": action,
        "target": target,
        "modifiers": modifiers,
        "components": components,
        "is_complex": is_complex,
    }


def _extract_action(text: str) -> str:
    words = text.split()
    for word in words:
        cleaned = word.strip(".,;:!?()[]{}'\"")
        if cleaned in ACTION_VERBS:
            return cleaned
    return "implement"


def _singularize(word: str) -> str:
    """Convert plural word to singular form using simple rules."""
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("ses") or word.endswith("xes") or word.endswith("zes") or word.endswith("ches") or word.endswith("shes"):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _normalize_to_base_form(word: str) -> str:
    """Normalize word to base form for matching against TARGET_NOUNS."""
    stripped = word.strip(".,;:!?()[]{}'\"")
    if not stripped:
        return stripped
    singular = _singularize(stripped)
    if stripped.endswith("ing") and len(stripped) > 4:
        base = stripped[:-3]
        if base + "e" in TARGET_NOUNS:
            return base + "e"
        if base in TARGET_NOUNS:
            return base
    return singular


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


def _normalize_modifier(modifier: str) -> str:
    from .proposer_criteria import _make_meaningful_condition
    result = modifier
    for prep in MODIFIER_PREPOSITIONS:
        if result.startswith(prep + " "):
            rest = result[len(prep):].strip()
            if rest:
                result = _make_meaningful_condition(rest, prep)
                break
    if not result or len(result) < 3:
        return "the necessary conditions are met"
    return result


__all__ = [
    "parse_intent",
    "_extract_action",
    "_extract_target",
    "_extract_modifiers",
    "_build_modifier_phrase",
    "_normalize_modifier",
    "_normalize_to_base_form",
    "_singularize",
]
