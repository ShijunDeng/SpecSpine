from __future__ import annotations

import re

__all__ = [
    "_BREAKING_CHANGE_PATTERNS",
]

_BREAKING_CHANGE_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(r"removed\s+(?:the\s+)?`(--?\S+)`", re.IGNORECASE),
        "high",
        "CLI argument removed",
    ),
    (
        re.compile(r"removed\s+(?:the\s+)?required\s+field", re.IGNORECASE),
        "high",
        "Required field removed",
    ),
    (
        re.compile(r"changed\s+(?:the\s+)?(?:default|behavior|validation|output)", re.IGNORECASE),
        "medium",
        "Default behavior changed",
    ),
    (
        re.compile(r"deprecated\s+(?:the\s+)?`(--?\S+)`", re.IGNORECASE),
        "low",
        "Deprecation introduced",
    ),
    (
        re.compile(r"renamed\s+(?:the\s+)?`(--?\S+)`", re.IGNORECASE),
        "medium",
        "Name change",
    ),
]
