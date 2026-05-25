from __future__ import annotations

from ._proposer_ui_nouns_aggregate_core import TARGET_NOUNS_UI_CORE
from ._proposer_ui_nouns_aggregate_extended import TARGET_NOUNS_UI_EXTENDED
from .proposer_ui_nouns_controls import TARGET_NOUNS_CONTROLS  # noqa: F401
from .proposer_ui_nouns_layouts import TARGET_NOUNS_LAYOUTS  # noqa: F401
from .proposer_ui_nouns_patterns import TARGET_NOUNS_PATTERNS  # noqa: F401

__all__ = [
    "TARGET_NOUNS_UI",
]

TARGET_NOUNS_UI = TARGET_NOUNS_UI_CORE + TARGET_NOUNS_UI_EXTENDED
