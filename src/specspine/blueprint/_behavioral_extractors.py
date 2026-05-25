from __future__ import annotations

import re

from ..proposer import TARGET_NOUNS
from .blueprint_models import (
    _BEHAVIORAL_VERBS,
    _NOUN_PHRASE_RE,
)


def _extract_behavioral_verb(text: str) -> str | None:
    lower = text.lower()
    for verb in _BEHAVIORAL_VERBS:
        if re.search(rf"\b{re.escape(verb)}\b", lower):
            return verb
    return None


def _extract_target_noun(text: str) -> str:
    lower = text.lower()
    for noun in TARGET_NOUNS:
        if re.search(rf"\b{re.escape(noun)}\b", lower):
            return noun
    match = _NOUN_PHRASE_RE.search(text)
    if match:
        return match.group(1).strip()
    return "component"


__all__ = [
    "_extract_behavioral_verb",
    "_extract_target_noun",
]
