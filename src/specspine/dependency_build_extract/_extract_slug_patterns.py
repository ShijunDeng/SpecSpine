"""Extract dependency slugs from text using pattern matching."""

from __future__ import annotations

from specspine.dependency_models import EXPLICIT_DEP_PATTERNS

__all__ = [
    "_extract_slugs_from_text",
]


def _extract_slugs_from_text(text: str, current_slug: str, valid_slugs: set[str] | None = None) -> list[str]:
    slugs: list[str] = []
    for pattern in EXPLICIT_DEP_PATTERNS:
        for match in pattern.finditer(text):
            found = match.group(1)
            if found != current_slug and found not in slugs:
                if valid_slugs is None or found in valid_slugs:
                    slugs.append(found)
    return slugs
