from __future__ import annotations

from ._verb_phonetics import _is_cvc, _is_stressed_syllable

__all__ = [
    "_conjugate_verb",
    "_to_gerund",
    "_to_past",
]


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
