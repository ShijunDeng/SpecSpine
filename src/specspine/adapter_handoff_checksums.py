from __future__ import annotations

import hashlib

__all__ = [
    "_sha256_hex",
]


def _sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
