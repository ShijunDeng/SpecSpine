from __future__ import annotations

from textwrap import dedent

__all__ = [
    "normalize_template",
]


def normalize_template(content: str) -> str:
    if not content:
        return content
    return dedent(content).strip() + "\n"
