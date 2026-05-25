from __future__ import annotations

import re

__all__ = [
    "EXPLICIT_DEP_PATTERNS",
]

EXPLICIT_DEP_PATTERNS = [
    re.compile(r"Feature\s+ID:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"depends\s+on\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"after\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"blocked\s+by\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"requires\s+([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
    re.compile(r"prerequisite:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE),
]
