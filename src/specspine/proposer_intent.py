from __future__ import annotations

import re

from .workspace import normalize_template

from .proposer_intent_constants import (
    ACTION_VERBS,
    COMPONENT_SPLITTERS,
    MAX_INTENT_CHARS,
    MODIFIER_PREPOSITIONS,
    STOP_WORDS,
    TARGET_NOUNS,
    InvalidProposalIntent,
)
from .proposer_intent_parsing import (
    _build_modifier_phrase,
    _extract_action,
    _extract_modifiers,
    _extract_target,
    _normalize_modifier,
    _normalize_to_base_form,
    _singularize,
    parse_intent,
)
from .proposer_intent_validation import (
    _truncation_warning,
    normalize_intent,
    validate_intent,
)


__all__ = [
    "InvalidProposalIntent",
    "MAX_INTENT_CHARS",
    "ACTION_VERBS",
    "TARGET_NOUNS",
    "MODIFIER_PREPOSITIONS",
    "COMPONENT_SPLITTERS",
    "STOP_WORDS",
    "normalize_intent",
    "validate_intent",
    "parse_intent",
    "_extract_action",
    "_extract_target",
    "_extract_modifiers",
    "_build_modifier_phrase",
    "_normalize_modifier",
    "_normalize_to_base_form",
    "_singularize",
    "_truncation_warning",
]
