from __future__ import annotations

import re

from .proposer_intent import validate_intent

__all__ = [
    "SLUG_STOP_WORDS",
    "generate_slug_from_intent",
    "_slug_to_title",
]

SLUG_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


def generate_slug_from_intent(intent: str) -> str:
    normalized = validate_intent(intent)
    tokens = re.findall(r"[a-z0-9]+", normalized.lower())
    filtered = [token for token in tokens if token not in SLUG_STOP_WORDS]
    selected = filtered[:5] or tokens[:5] or ["proposal"]
    slug = "-".join(selected)

    if not slug[0].isalnum():
        slug = f"proposal-{slug}"
    if not slug[-1].isalnum():
        slug = f"{slug}-proposal"

    from .features import validate_feature_slug

    return validate_feature_slug(slug)


def _slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").title()
