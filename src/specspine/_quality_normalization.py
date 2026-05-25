from __future__ import annotations

import re

__all__ = [
    "_normalized_criterion_text",
]


def _normalized_criterion_text(text: str) -> str:
    normalized = re.sub(r"`([^`]*)`", r"\1", text.lower())
    normalized = re.sub(r"\b(ac[-\s]?0*\d+|must|should|shall)\b", " ", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()
