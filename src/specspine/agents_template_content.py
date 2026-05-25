from __future__ import annotations

from ._template_header import _TEMPLATE_HEADER
from ._template_commands import _TEMPLATE_COMMANDS
from ._template_rules import _TEMPLATE_RULES

__all__ = [
    "AGENTS_TEMPLATE",
]

AGENTS_TEMPLATE = _TEMPLATE_HEADER + _TEMPLATE_COMMANDS + _TEMPLATE_RULES
