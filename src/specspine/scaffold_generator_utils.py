from __future__ import annotations

import re

SLUG_TO_CLASS_RE = re.compile(r"(?:^|-)([a-z])")
AC_KEYWORD_RE = re.compile(r"(?:can|should|must|will|shall|is|are)\s+(\S+)")

__all__ = [
    "_ac_id_snake",
    "_extract_ac_keyword",
    "_slug_to_camel",
]


def _slug_to_camel(slug: str) -> str:
    def _repl(match: re.Match[str]) -> str:
        return match.group(1).upper()
    result = SLUG_TO_CLASS_RE.sub(_repl, slug)
    if result and result[0].islower():
        result = result[0].upper() + result[1:]
    return result


def _ac_id_snake(ac_id: str) -> str:
    return ac_id.lower()


def _extract_ac_keyword(ac_text: str) -> str:
    match = AC_KEYWORD_RE.search(ac_text)
    if match:
        return match.group(1).lower()
    words = ac_text.strip().split()
    if words:
        return words[0].lower()
    return "behavior"
