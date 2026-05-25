from __future__ import annotations

import re

__all__ = [
    "ARCHIVE_ID_RE",
    "TEST_COVERAGE_HEADING_RE",
]

ARCHIVE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
TEST_COVERAGE_HEADING_RE = re.compile(
    r"^#{2,6}\s+Test Coverage\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
