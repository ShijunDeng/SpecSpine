from __future__ import annotations

from ..proposer_intent_validation import validate_intent
from ..proposer_intent_constants import COMPONENT_SPLITTERS
from ._parsing_extractors import _extract_action, _extract_target, _extract_modifiers

__all__ = [
    "parse_intent",
]


def parse_intent(intent: str) -> dict:
    text = validate_intent(intent).lower()

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
