from __future__ import annotations

import re

from .blueprint_models import (
    _ENTITY_INDICATORS,
    _NOUN_PHRASE_RE,
)

__all__ = [
    "_extract_entity_name",
]


def _extract_entity_name(
    text: str,
    target: str,
) -> str | None:
    entity_name: str | None = None
    for indicator in _ENTITY_INDICATORS:
        pattern = re.compile(rf"\b(?:the\s+)?(\w+)\s+{indicator}", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            candidate = match.group(1).lower()
            if candidate not in ("a", "an", "the", "new", "one", "any", "each", "every", "some", "another"):
                entity_name = candidate
                break
    if entity_name is None:
        if target and target not in ("a", "an", "the", "new"):
            entity_name = target
        else:
            match = _NOUN_PHRASE_RE.search(text)
            if match:
                entity_name = match.group(1).strip().lower().split()[0]
            else:
                return None
    return entity_name
