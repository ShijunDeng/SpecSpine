from __future__ import annotations

import re

__all__ = [
    "DOCUMENTATION_GLOBS",
    "IMPLEMENTATION_GLOBS",
    "LOCAL_PATH_RE",
    "TEST_GLOBS",
]

LOCAL_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"(?P<path>(?:src|tests|docs|specs|execution|quality)/[A-Za-z0-9_./-]+|README\.md|AGENTS\.md)"
)

IMPLEMENTATION_GLOBS = ("src/**/*.py",)
TEST_GLOBS = ("tests/**/*.py",)
DOCUMENTATION_GLOBS = (
    "docs/**/*.md",
    "README.md",
    "AGENTS.md",
    "specs/*.md",
    "execution/*.md",
    "quality/*.md",
)
