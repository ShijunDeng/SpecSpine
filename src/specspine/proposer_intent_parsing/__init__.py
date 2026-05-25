from __future__ import annotations

from ._parsing_core import parse_intent
from ._parsing_extractors import (
    _build_modifier_phrase,
    _extract_action,
    _extract_modifiers,
    _extract_target,
)
from ._parsing_normalization import (
    _normalize_modifier,
    _normalize_to_base_form,
    _singularize,
)

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
