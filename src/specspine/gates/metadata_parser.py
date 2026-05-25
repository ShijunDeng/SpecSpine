from __future__ import annotations

import re
from typing import Match

from .constants import (
    METADATA_TAG_RE,
    SUPPORTED_SEVERITIES,
)

__all__ = [
    "_parse_gate_metadata",
]


def _parse_gate_metadata(raw_text: str) -> tuple[
    str,
    str,
    str,
    str | None,
    dict[str, str],
    tuple[str, ...],
]:
    metadata: dict[str, str] = {}
    warnings: list[str] = []
    severity = "medium"
    owner = "unassigned"
    ci_check: str | None = None

    def replace_tag(match: Match[str]) -> str:
        nonlocal severity, owner, ci_check

        raw_key, raw_value = match.groups()
        key = raw_key.lower()
        value = raw_value.strip()
        if key not in {"severity", "owner", "ci"}:
            return match.group(0)

        if key == "severity":
            normalized = value.lower()
            metadata[key] = normalized
            if normalized in SUPPORTED_SEVERITIES:
                severity = normalized
            else:
                warnings.append(f"unsupported severity: {value}")
            return " "

        if key == "owner":
            if value:
                owner = value
                metadata[key] = value
            return " "

        if value:
            ci_check = value
            metadata[key] = value
        return " "

    cleaned_text = METADATA_TAG_RE.sub(replace_tag, raw_text).strip()
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)
    return cleaned_text, severity, owner, ci_check, metadata, tuple(warnings)
