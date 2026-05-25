from __future__ import annotations

import re

__all__ = [
    "FEATURE_ID_RE",
    "DEPENDENCY_PATTERNS",
]

FEATURE_ID_RE = re.compile(r"Feature\s+ID:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
DEPENDENCY_PATTERNS = [
    re.compile(r"depends\s+on\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"after\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"blocked\s+by\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"requires\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
]
