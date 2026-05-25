from __future__ import annotations

from .proposer_verbs_table import IRREGULAR_VERBS

__all__ = [
    "_get_action_verb_form",
    "_conjugate_verb",
    "_to_gerund",
    "_to_past",
    "_is_cvc",
    "_is_stressed_syllable",
]


def _get_action_verb_form(action: str, form: str = "base") -> str:
    """Convert action verb to appropriate grammatical form."""
    if action in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[action].get(form, action)
    return _conjugate_verb(action, form)


def _conjugate_verb(verb: str, form: str) -> str:
    """Apply English conjugation rules for verbs not in the explicit table."""
    if form == "base":
        return verb
    if form == "gerund":
        return _to_gerund(verb)
    if form == "past":
        return _to_past(verb)
    return verb


def _to_gerund(verb: str) -> str:
    """Convert verb to gerund (-ing) form."""
    if not verb:
        return verb
    if verb.endswith("ie"):
        return verb[:-2] + "ying"
    if verb.endswith("ee"):
        return verb + "ing"
    if verb.endswith("e") and not verb.endswith("ee"):
        return verb[:-1] + "ing"
    if len(verb) >= 3 and _is_cvc(verb) and _is_stressed_syllable(verb):
        return verb + verb[-1] + "ing"
    return verb + "ing"


def _to_past(verb: str) -> str:
    """Convert verb to past tense (-ed) form."""
    if not verb:
        return verb
    if verb.endswith("e"):
        return verb + "d"
    if verb.endswith("y") and len(verb) >= 2 and verb[-2] not in "aeiou":
        return verb[:-1] + "ied"
    if len(verb) >= 3 and _is_cvc(verb) and _is_stressed_syllable(verb):
        return verb + verb[-1] + "ed"
    return verb + "ed"


def _is_cvc(word: str) -> bool:
    """Check if word ends in consonant-vowel-consonant pattern."""
    if len(word) < 3:
        return False
    vowels = set("aeiou")
    return (word[-3] not in vowels and
            word[-2] in vowels and
            word[-1] not in vowels)


def _is_stressed_syllable(word: str) -> bool:
    """Heuristic: single syllable or stress on last syllable."""
    if len(word) <= 2:
        return True
    vowels = set("aeiou")
    vowel_count = sum(1 for c in word.lower() if c in vowels)
    return vowel_count <= 2
