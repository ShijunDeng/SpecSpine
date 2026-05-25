from __future__ import annotations

import re

__all__ = [
    "_extract_attributes",
]


def _extract_attributes(text: str) -> list[str]:
    attrs: list[str] = []
    words = text.split()
    for i, word in enumerate(words):
        if word.lower() in ("with", "has", "containing", "including"):
            rest = " ".join(words[i + 1:])
            parts = re.split(r"\band\b|,|\bor\b", rest)
            for part in parts:
                cleaned = part.strip().rstrip(".")
                if cleaned and len(cleaned) > 2:
                    attrs.append(cleaned.replace(" ", "_"))
    return attrs
