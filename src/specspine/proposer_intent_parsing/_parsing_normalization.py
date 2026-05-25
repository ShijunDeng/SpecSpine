from __future__ import annotations

from ..proposer_intent_constants import TARGET_NOUNS, MODIFIER_PREPOSITIONS

__all__ = [
    "_normalize_modifier",
    "_normalize_to_base_form",
    "_singularize",
]


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


def _normalize_modifier(modifier: str) -> str:
    from ..proposer_criteria import _make_meaningful_condition
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
