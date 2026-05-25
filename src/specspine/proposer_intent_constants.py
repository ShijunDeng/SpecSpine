from __future__ import annotations

from .proposer_intent_verbs import *
from .proposer_intent_nouns import *
from .proposer_intent_patterns import *

__all__ = [
    "InvalidProposalIntent",
    "MAX_INTENT_CHARS",
    "ACTION_VERBS",
    "TARGET_NOUNS",
    "MODIFIER_PREPOSITIONS",
    "COMPONENT_SPLITTERS",
    "STOP_WORDS",
]
