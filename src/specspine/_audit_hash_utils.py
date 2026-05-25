from __future__ import annotations

import hashlib

__all__ = [
    "_hash_content",
]


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
